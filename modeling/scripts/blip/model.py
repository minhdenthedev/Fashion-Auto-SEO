from transformers import AutoProcessor, BlipForConditionalGeneration

def prepare_model(freeze_vit=False, freeze_bert=False):
    # load model and processor
    processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    # freeze parameters of ViT
    if freeze_vit:
        for parameter in model._modules['vision_model'].parameters():
            parameter.requires_grad = False

    if freeze_bert:
        for parameter in model._modules['text_decoder'].parameters():
            parameter.requires_grad = False

    return model, processor