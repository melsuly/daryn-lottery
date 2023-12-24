import os
from PIL import ImageFont, Image, ImageDraw, ImageOps
from io import BytesIO
import json

artists_without_pictures = []
artists_json = []

artist_json = {
    "name": "",
    "picture": "",
    "audio": ""
}


def divide_into_sub_arrays(files, max_elements=4):
    sub_arrays = []
    for i in range(0, len(files), max_elements):
        sub_arrays.append(files[i:i + max_elements])
    return sub_arrays


def get_font_bytes(filename):
    with open(filename, 'rb') as f:
        return BytesIO(f.read())


def get_music_files():
    excluded_files = ['.ds_store', '.', '..']

    files = [f.path.split('/')[-1] for f in os.scandir(
        'public/audio') if f.is_file() and f.name.lower() not in excluded_files]

    files.sort()

    return files


def get_name(filename):
    return filename.split('.')[0]


def get_ticket_number(number):
    return str(number).zfill(3)


def clear_output_folder():
    for f in os.scandir('design/tickets'):
        os.remove(f.path)


def draw_name(artist_name):
    colors = {
        "green": "#0bd65c",
        "yellow": "#d7de1d",
        "red": "#e3092a"
    }
    font_montserrat = ImageFont.truetype(get_font_bytes(
        "src/assets/fonts/montserrat-black.ttf"
    ), 40)
    plate_color = colors["green"]

    artist_json["audio"] = "{}.mp3".format(artist_name)

    if artist_name[0] == "!":
        artist_name = artist_name[1:]
        plate_color = colors["yellow"]

        if artist_name[0] == "!":
            artist_name = artist_name[1:]
            plate_color = colors["red"]

    artist_json["name"] = artist_name

    plate = Image.new('RGB', (877, 70), color=plate_color)
    draw = ImageDraw.Draw(plate)

    draw.text((30, 10), artist_name.upper(),
              font=font_montserrat, fill=("#fff"))

    plate = plate.rotate(90, expand=True)

    return plate


def draw_image(artist_name: str):
    image_formats = ["png", "jpg", "jpeg"]
    image = Image.new('L', (757, 877), ("#fff"))
    artist_name = artist_name.removeprefix("!")
    artist_name = artist_name.removeprefix("!")
    is_found = False

    for format in image_formats:
        image_filename = "public/avatar/{}.{}".format(artist_name, format)

        if os.path.isfile(image_filename):
            try:
                image = Image.open(image_filename)

                image = ImageOps.fit(image, (757, 877))

                is_found = True

                artist_json["picture"] = image_filename
            except:
                pass

            break

    if not is_found:
        artists_without_pictures.append(artist_name)

    return image


def generate_tickets(files):
    font_bebas = ImageFont.truetype(get_font_bytes(
        'src/assets/fonts/bebas-neue.ttf'), 140)

    ticket_number = 1
    ticket_portions = divide_into_sub_arrays(files)

    clear_output_folder()

    for i, ticket_portion in enumerate(ticket_portions):
        template = Image.open('design/template.png')
        draw = ImageDraw.Draw(template)

        for j, artist in enumerate(ticket_portion):
            artist_name = get_name(artist)

            draw.text((452, 625 + (878 * j)), get_ticket_number(
                ticket_number), font=font_bebas, fill=("#fff"))
            template.paste(draw_name(artist_name), (1653, 877 * j))
            template.paste(draw_image(artist_name), box=(1723, 877 * j))

            ticket_number += 1
            artists_json.append(artist_json.copy())

        template.save('design/tickets/tickets_{}.png'.format(i + 1))
        print("Part {} of {} generated!".format(i + 1, len(ticket_portions)))


if __name__ == '__main__':
    files = get_music_files()

    print("Successfully scanned {} files!".format(len(files)))

    print("Generating tickets...")

    generate_tickets(files)

    if artists_without_pictures:
        print("Artists without pictures: {}".format(
            ", ".join(artists_without_pictures)))

    print("Writing artists.json...")

    with open('src/data/artists.json', 'w') as outfile:
        json.dump(artists_json, outfile, ensure_ascii=False)

    print("Done!")
