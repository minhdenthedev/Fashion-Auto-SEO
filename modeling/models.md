# Model checkpoints

## 1. English caption
#### Train dataset: H&M Product Captioning
    - Link: https://huggingface.co/datasets/tomytjandra/h-and-m-fashion-caption
#### Test dataset: 
    - Link: https://huggingface.co/datasets/wbensvage/clothes_desc
    
#### Checkpoints: 
    All versions of model weights is on https://huggingface.co/kzap201/fashion_BLIP
    To load model from huggingface, use:
    ```python
    from transformers import BlipForConditionalGeneration

    model = BlipForConditionalGeneration.from_pretrained(
        'kzap201/fashion_BLIP',
        revision='<version>'  # Replace <version> with the desired checkpoint version
    )
    ```

    |  Date       | Version   | BLEU-1 | BLEU-2 | BLEU-3 | BLEU-4 | METEOR | ROUGE-L |
    |-------------|-----------|--------|--------|--------|--------|--------|---------|
    |  05/04/2025 | v1.0      | 0.506  | 0.407  | 0.337  | 0.287  | 0.284  | 0.494   |
    |  06/04/2025 | v2.0      | 0.511  | 0.411  | 0.341  | 0.289  | 0.293  | 0.506   |
        
## 2. Vietnamese caption
Not yet