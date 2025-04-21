# Model checkpoints

## 1. English caption
#### Train dataset: H&M Product Captioning
    - Link: https://huggingface.co/datasets/tomytjandra/h-and-m-fashion-caption
#### Test dataset: 
    - Link: https://huggingface.co/datasets/wbensvage/clothes_desc

    ![Alt text](imgs/samples1.png)
    ![Alt text](imgs/samples2.png)
    ![Alt text](imgs/samples3.png)
    
#### Checkpoints:
    - 05/04/2025 (End-to-end trainging): 
        - Test CIDEr: 1.70
        - Link (click to download): https://huggingface.co/kzap201/BLIP_pretrained_on_H_and_M_captions/resolve/main/best_checkpoint.pth?download=true
    - 06/04/2025 (Freeze ViT):
        - Test CIDEr: 1.78
        - Link (click to download): https://huggingface.co/kzap201/BLIP_pretrained_on_H_and_M_captions/resolve/main/best_checkpoint_freeze_vit.pth?download=true

## 2. Vietnamese caption
Not yet