import torch
from data_loading import prepare_data
from model import prepare_model
from tqdm import tqdm
from accelerate import Accelerator
from metrics import cider_score
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
import argparse
        
def save_checkpoint(save_path, model, epoch, best_metric, optimizer=None, lr_scheduler=None):
    checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': lr_scheduler.state_dict(),
            'best_cider': best_metric
        }
    torch.save(checkpoint, save_path)

def train_blip(
    num_epochs, batch_size, train_size, lr=5e-5, weight_decay=0.01,
    caption_max_length=35,
    freeze_vit=False, freeze_bert=False, 
    checkpoint_path=None, checkpoint_savepath=None
):
    # metrics
    best_cider = 0.0   # can be changed if load checkpoint

    # prepare model
    model, processor = prepare_model(freeze_vit=freeze_vit, freeze_bert=freeze_bert)
    
    # prepare data
    train_loader, val_loader = prepare_data(
        dataset='tomytjandra/h-and-m-fashion-caption', data_processor=processor,
        train_size=train_size, batch_size=batch_size
    )
    
    # optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    # lr scheduler
    lr_scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=5, T_mult=2)
    
    # continue from checkpoint if specify
    if checkpoint_path is not None:
        checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        lr_scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        epoch = checkpoint['epoch']
        best_cider = checkpoint['best_cider']
        print(f"Checkpoint loaded: Resuming from Epoch {epoch}, best_cider={best_cider}")


    # TRAINING LOOPS
    
    # accelerator to use dual gpu
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    accelerator = Accelerator()
    train_loader, val_loader, model, optimizer, lr_scheduler = accelerator.prepare(
            train_loader, val_loader, model, optimizer, lr_scheduler 
    )
    
    for epoch in range(num_epochs):
        model.train()
        train_loops = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}:')
        epoch_loss = 0.0
        for i, batch in enumerate(train_loops):
            input_ids = batch.pop("input_ids").to(device)
            pixel_values = batch.pop("pixel_values").to(device)
    
            outputs = model(input_ids=input_ids,
                            pixel_values=pixel_values,
                            labels=input_ids)
    
            loss = outputs.loss
            accelerator.backward(loss)
            optimizer.step()
            optimizer.zero_grad()

            # update lr scheduler
            lr_scheduler.step(epoch + i / len(train_loader))
    
            # visualize batch loss
            all_gpu_loss = accelerator.gather(loss).mean().item()
            epoch_loss += all_gpu_loss
        epoch_loss /= len(train_loader)
    
        # evaluate
        model.eval()
        with torch.no_grad():
            ## val set                                                                          
            eval_loops = tqdm(val_loader, desc=f'Validating epoch {epoch+1}/{num_epochs}:')
            val_loss = 0.0
            ground_truth = []
            generated = []
            for batch in eval_loops:
                input_ids = batch.pop("input_ids").to(device)
                pixel_values = batch.pop("pixel_values").to(device)
    
                outputs = model(input_ids=input_ids,
                            pixel_values=pixel_values,
                            labels=input_ids)
                
                # ground truth
                gt_captions = processor.batch_decode(input_ids, skip_special_tokens=True)
                ground_truth.extend(gt_captions)
                # generated
                generated_ids = model.module.generate(pixel_values=pixel_values, max_length=caption_max_length)
                generated_captions = processor.batch_decode(generated_ids, skip_special_tokens=True)
                generated.extend(generated_captions)
            
                # loss
                loss = outputs.loss
                all_gpu_loss = accelerator.gather(loss).mean().item()
                val_loss += all_gpu_loss
            val_loss /= len(val_loader)
            val_cider = cider_score(ground_truth, generated)
        
            # log
            print(f'Epoch {epoch+1}/{num_epochs}: train_loss={epoch_loss:.4f}, val_loss={val_loss:.4f}, val_cider={val_cider:.4f}')
    
            # save check point
            if val_cider > best_cider:
                unwrapped_model = accelerator.unwrap_model(model)
                best_cider = val_cider
                if checkpoint_savepath is not None:
                    save_checkpoint(f'{checkpoint_savepath}/best.pth', unwrapped_model,
                                    epoch+1, best_cider, optimizer, lr_scheduler)
                else:
                    save_checkpoint('best.pth', unwrapped_model,
                                    epoch+1, best_cider, optimizer, lr_scheduler)
                print(f"Best checkpoint saved at epoch {epoch+1}")
    
    else:
        unwrapped_model = accelerator.unwrap_model(model)
        save_checkpoint('/kaggle/working/last.pth', unwrapped_model, 
                            epoch+1, best_cider, optimizer, lr_scheduler)
        print(f"Last checkpoint saved.")
    

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Train BLIP model on H&M dataset")
    parser.add_argument("--num_epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size for training")
    parser.add_argument("--train_size", type=float, default=0.8, help="Proportion of training data")
    parser.add_argument("--lr", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--weight_decay", type=float, default=0.01, help="Weight decay for optimizer")
    parser.add_argument("--caption_max_length", type=int, default=50, help="Maximum length of generated captions")
    parser.add_argument("--freeze_vit", action="store_true", help="Freeze Vision Transformer layers")
    parser.add_argument("--freeze_bert", action="store_true", help="Freeze BERT layers")
    parser.add_argument("--checkpoint_path", type=str, default=None, help="Path to checkpoint for resuming training")
    parser.add_argument("--checkpoint_savepath", type=str, default=None, help="Path to save checkpoint")

    args = parser.parse_args()

    # Extract arguments from parser
    num_epochs = args.num_epochs
    batch_size = args.batch_size
    train_size = args.train_size
    lr = args.lr
    weight_decay = args.weight_decay
    caption_max_length = args.caption_max_length
    freeze_vit = args.freeze_vit
    freeze_bert = args.freeze_bert
    checkpoint_path = args.checkpoint_path
    checkpoint_savepath = args.checkpoint_savepath

    train_blip(num_epochs=num_epochs, batch_size=batch_size, train_size=train_size, lr=lr, weight_decay=weight_decay,
                caption_max_length=caption_max_length,
                freeze_vit=freeze_vit, freeze_bert=freeze_bert, 
                checkpoint_path=checkpoint_path, checkpoint_savepath=checkpoint_savepath
    )