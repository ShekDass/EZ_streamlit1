import re
import transformers
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import random
import numpy as np

# hide logs
transformers.logging.disable_default_handler()

# Load our model from Hugging Face
processor = DonutProcessor.from_pretrained("ShekDass/donut-base-cord-smart-86")
model = VisionEncoderDecoderModel.from_pretrained("ShekDass/donut-base-cord-smart-86")

# Move model to GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Load PRODUCTION Image Sample
# test_sample = processed_dataset["test"][random.randint(0, len(processed_dataset["test"]) - 1)]
# prod_image = rgb_testsample

def image_to_json(image, model=model, processor=processor):
    # prepare inputs
    # pixel_values = torch.tensor(test_sample["pixel_values"]).unsqueeze(0)
    # pixel_values = processor(prod_image, return_tensors="pt").pixel_values
    pixel_values = processor(image, return_tensors="pt").pixel_values
    print(pixel_values.shape)
    task_prompt = "<s>"
    decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids

    # run inference
    outputs = model.generate(
        pixel_values.to(device),
        decoder_input_ids=decoder_input_ids.to(device),
        max_length=model.decoder.config.max_position_embeddings,
        early_stopping=True,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        num_beams=1,
        bad_words_ids=[[processor.tokenizer.unk_token_id]],
        return_dict_in_generate=True,
    )

    # process output
    prediction = processor.batch_decode(outputs.sequences)[0]
    prediction = prediction.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
    prediction = re.sub(r"<.*?>", "", prediction, count=1).strip()  # remove first task start token
    prediction = processor.token2json(prediction)

    # load reference target
    # target = processor.token2json(test_sample["target_sequence"])
    # return prediction, target
    return prediction
