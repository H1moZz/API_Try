from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import shutil

app = Flask(__name__)


os.makedirs('result_folder', exist_ok=True)
os.makedirs('upload_folder', exist_ok=True)

def clear_res_folder():
    result_path = os.path.abspath('result_folder')
    for filename in os.listdir(result_path):  
        file_path = os.path.join(result_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print(f"Удален файл: {file_path}")  
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  
        except Exception as e:
            print(f'Не удалось удалить {file_path}. Причина: {e}')

@app.route('/generate-tickets', methods=['POST'])
def generate_tickets():

    if 'template' not in request.files:
        return jsonify({"error": "Необходимо загрузить файл шаблона"}), 400

    file = request.files['template']
    if not file or not file.filename:
        return jsonify({"error":"Файл шаблона не найден"}), 400

    template_path = os.path.join('upload_folder', f"{file.filename}")
    file.save(template_path)

    data = request.form
    promocodes = data.get('promocodes')
    if not promocodes:
        return jsonify({"error": "Необходимо указать список промокодов"}), 400
    promocodes = promocodes.split(" ")

    font_path = data.get('font_path', 'arial.ttf')
    font_size = int(data.get('font_size', 36))  
    text_x = int(data.get('text_x', 250))
    text_y = int(data.get('text_y', 680))

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        return jsonify({"error": f"Ошибка загрузки шрифта: {str(e)}"}), 400

    images = []
    for i, promocode in enumerate(promocodes):
        with Image.open(template_path) as img:
            draw = ImageDraw.Draw(img)
            draw.text((text_x,text_y), promocode, font=font, fill='black')
            
            img.save(os.path.join('result_folder', f'ticket_{i + 1}.png'))
            images.append(img.convert('RGB'))
    
    pdf_name = 'Promo.pdf'
    result_path = os.path.abspath('result_folder')
    pdf_path = os.path.join(result_path, pdf_name)
    print(f'Path: {pdf_path}')
    
    if images:
        images[0].save(pdf_path, save_all=True, append_images=images[1:])

    os.remove(template_path)

    response = send_file(pdf_path, as_attachment=True, download_name="Promo.PDF", mimetype='application/pdf')

    clear_res_folder()

    return response


@app.route('/')
def Home():
    return "Home page"

if __name__ == '__main__':
    app.run(debug=True)

