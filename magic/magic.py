import os
from optparse import OptionParser
from io import BytesIO
from PIL import Image, ImageOps
from django.utils import six


def pil_image(input_f, quality=80):
    if isinstance(input_f, six.string_types):
        filename = input_f
    elif hasattr(input_f, 'name'):
        filename = input_f.name
    else:
        filename = 'noname.png'

    extension = os.path.splitext(filename)[-1].lower()
    try:
        format = {
            '.jpg': 'jpeg',
            '.jpeg': 'jpeg',
            '.png': 'png',
            '.gif': 'gif',
        }[extension]
    except KeyError:
        format = 'png'

    image = Image.open(input_f)
    return image, format


def image_to_file(image, format, quality):
    output_f = BytesIO()
    image.save(output_f, format=format, quality=quality)
    output_f.seek(0)
    return output_f


def thumbnail(input_f, width, height, quality=80):
    image, format = pil_image(input_f, quality)
    image.thumbnail((width, height), Image.ANTIALIAS)
    return image_to_file(image, format, quality)


def square_image(input_f, max_size, quality=80):
    image, format = pil_image(input_f, quality)
    max_size = min(image.size[0], image.size[1], max_size)
    image = ImageOps.fit(image, size=(max_size, max_size))
    return image_to_file(image, format, quality)


if __name__ == '__main__':
    usage = 'usage: %prog [options] imagefile1'

    parser = OptionParser(usage=usage)
    parser.add_option('-t', '--thumbnail', action='store_const', const='thumbnail', dest='type',
                      default='thumbnail', help='create thumbnail image')
    parser.add_option('-s', '--square', action='store_const', const='square', dest='type',
                      help='create square image')
    parser.add_option('-w', '--width', type='int', dest='width', default=800)
    parser.add_option('-q', '--quality', type='int', dest='quality', default=80)

    (options, args) = parser.parse_args()

    for src_filename in args:
        with open(src_filename, 'rb') as input_f:
            if options.type == 'thumbnail':
                dest_f = thumbnail(input_f, options.width, options.width, options.quality)
            elif options.type == 'square':
                dest_f = square_image(input_f, options.width, options.quality)

            postfix = '_{}_{}_{}'.format(options.type, options.width, options.quality)

            splitted_ext = os.path.splitext(src_filename)
            dest_filename = ''.join((splitted_ext[0], postfix, splitted_ext[1]))

            open(dest_filename, 'wb').write(dest_f.read())
            print('created {}'.format(dest_filename))