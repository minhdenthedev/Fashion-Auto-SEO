import requests
import json
import os

def download_images(metadata_file, save_path):
    assert os.path.exists(metadata_file), f"Metadata file {metadata_file} does not exist."
    assert os.path.exists(save_path), f"Save path {save_path} does not exist."

    with open(metadata_file, "r") as file:
        image_type = os.path.splitext(os.path.basename(metadata_file))[0]
        if not os.path.exists(os.path.join(save_path, image_type)):
            os.mkdir(os.path.join(save_path, image_type))
        data = json.load(file)

        count = 0
        captions = {}
        for i, d in enumerate(data):
            image_url = d["image_url"]
            image_data = requests.get(image_url).content

            image_name = image_type + f'_{i}.jpg'
            with open(f"{save_path}/{image_type}/{image_name}", "wb") as img:
                img.write(image_data)

            # save caption
            captions[image_name] = d["caption"]

            print(f"Downloaded {image_name}")
            count += 1

        with open(save_path + f'/{image_type}_captions.json', 'w') as captions_file:
            captions_file.write(json.dumps(captions))
            
        print(f"Downloaded {count} {image_type} images successfully.")

if __name__ == "__main__":
    metadata_path = '/teamspace/studios/this_studio/Fashion-Auto-SEO/modeling/data/raw/2025-03-02'
    save_path = '/teamspace/studios/this_studio/Fashion-Auto-SEO/modeling/data/raw'
    download_images(os.path.join(metadata_path, 'ao_lien_quan.json'), save_path)
    download_images(os.path.join(metadata_path, 'ao_so_mi_nu.json'), save_path)
    download_images(os.path.join(metadata_path, 'ao_thun_nu.json'), save_path)
    download_images(os.path.join(metadata_path, 'ao_vest_nu.json'), save_path)
    download_images(os.path.join(metadata_path, 'chan_vay_nu.json'), save_path)
    download_images(os.path.join(metadata_path, 'croptop.json'), save_path)
    download_images(os.path.join(metadata_path, 'dam_nu.json'), save_path)
    download_images(os.path.join(metadata_path, 'do_bau.json'), save_path)
    download_images(os.path.join(metadata_path, 'do_boi_nu.json'), save_path)
    download_images(os.path.join(metadata_path, 'do_lot_nu.json'), save_path)
    download_images(os.path.join(metadata_path, 'do_ngu_nu.json'), save_path)
    download_images(os.path.join(metadata_path, 'quan_nu.json'), save_path)
    download_images(os.path.join(metadata_path, 'trung_nien_nu.json'), save_path)