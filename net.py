import torch
import torchvision.transforms as transforms
import cv2
import numpy as np

# Load a pre-trained lightweight DehazeNet (converted to ONNX or PyTorch)
model = torch.jit.load("dehazenet_cpu.pt")
model.eval()  # Set model to evaluation mode

def dehaze_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Normalize and preprocess
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((256, 256)),
        transforms.Normalize((0.5,), (0.5,))
    ])
    input_tensor = transform(img).unsqueeze(0)  # Add batch dimension

    # Run model on CPU
    with torch.no_grad():
        output = model(input_tensor)

    # Convert back to image
    output_img = output.squeeze().numpy().transpose(1, 2, 0)
    output_img = (output_img * 255).astype(np.uint8)
    return output_img

dehazed = dehaze_image("hazy_image.jpg")
cv2.imwrite("dehazed_output.jpg", cv2.cvtColor(dehazed, cv2.COLOR_RGB2BGR))
