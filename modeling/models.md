# Model checkpoints

## 1. English caption
#### Train dataset: H&M Product Captioning
    - Link: https://huggingface.co/datasets/tomytjandra/h-and-m-fashion-caption
#### Test dataset: 
    - Link: https://huggingface.co/datasets/wbensvage/clothes_desc
    
#### Checkpoints: 
    All versions of model weights is on https://huggingface.co/kzap201/fashion_BLIP
    To load model from huggingface, use:
    `transformers.BlipForConditionalGeneration.from_pretrained('kzap201/fashion_BLIP', revision=<version>)`
    - 05/04/2025: v1.0 (End-to-end trainging) 
        - Test CIDEr: 1.70
    - 06/04/2025: v2.0 (Freeze ViT)
        - Test CIDEr: 1.78
        
## 2. Vietnamese caption
Not yet