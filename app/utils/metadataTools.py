from PIL import Image
from PIL.ExifTags import TAGS
import PyPDF2
import shutil
import pyexiv2
import ast
import locale
import sys

if sys.platform.startswith('win'):
    from docx import Document

def get_metadata(file_path):

    if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
        metadata = get_image_metadata(file_path)
    elif file_path.lower().endswith('.pdf'):
        metadata = get_pdf_metadata(file_path)
    elif file_path.lower().endswith('.docx') and sys.platform.startswith('win'):
        metadata = get_word_metadata(file_path)

    return metadata
    


def get_image_metadata(file_path):
    with pyexiv2.Image(file_path, encoding=str(locale.getpreferredencoding())) as img:
        metadata_exif = img.read_exif()
        metadata_xmp = img.read_xmp()
        metadata_iptc = img.read_iptc()
    metadata = {**metadata_exif, **metadata_xmp, **metadata_iptc}

    return metadata

def get_pdf_metadata(file_path):
    metadata = {}
    with open(file_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        doc_info = pdf.metadata
        metadata = {key[1:]: value for key, value in doc_info.items()}  # 移除前缀'/'，如'/Author'变为'Author'
    return metadata


def get_word_metadata(file_path):
    metadata = {}
    doc = Document(file_path)
    prop = doc.core_properties
    metadata = {}
    for d in dir(prop):
        if not d.startswith('_'):
            metadata[d] = getattr(prop, d)
    return metadata


def modify_metadata_and_save(file_path, new_metadata, save_path):
    """
    修改文件的元数据并保存为新文件。
    :param file_path: 原始文件的路径。
    :param new_metadata: 一个字典，包含要更新的元数据。
    :param save_path: 新文件的保存路径。
    """
    if file_path.lower().endswith(('.jpg', '.jpeg')):
        modify_image_metadata(file_path, new_metadata, save_path)
    elif file_path.lower().endswith('.pdf'):
        modify_pdf_metadata(file_path, new_metadata, save_path)
    elif file_path.lower().endswith('.docx') and sys.platform.startswith('win'):
        modify_word_metadata(file_path, new_metadata, save_path)
    else:
        print("Unsupported file type.")

def modify_image_metadata(file_path, new_metadata, save_path):
    """
    修改图像文件的元数据并保存为新文件。
    """
    shutil.copy(file_path, save_path)

    with pyexiv2.Image(save_path, encoding=str(locale.getpreferredencoding())) as img:
        current_metadata = {**img.read_exif(), **img.read_xmp(), **img.read_iptc()}
        
        # 确定需要更新的元数据项
        updates = {}
        for tag, new_value in new_metadata.items():
            current_value = current_metadata.get(tag)
            # 如果当前值不存在或与新值不同，则更新
            if new_value != '':
                if type(current_value) == type(new_value):
                    new_value = new_value
                    
                # 如果current_value是数值，直接强转new_value
                elif isinstance(current_value, (int, float)):
                    new_value = type(current_value)(new_value)
                # 对于其他复杂类型，使用literal_eval解析
                else:
                    new_value = ast.literal_eval(new_value)  

            if new_value != current_value:
                updates[tag] = new_value
        
        # 更新元数据
        for tag, value in updates.items():
            if tag.startswith('Exif'):
                img.modify_exif({tag: value})
            elif tag.startswith('Xmp'):
                img.modify_xmp({tag: value})
            elif tag.startswith('Iptc'):
                img.modify_iptc({tag: value})
        

def modify_pdf_metadata(file_path, new_metadata, save_path):
    """
    修改PDF文件的元数据并保存为新文件。
    """
    with open(file_path, 'rb') as infile:
        reader = PyPDF2.PdfReader(infile)
        writer = PyPDF2.PdfWriter()
        
        # 将所有页面从读取器复制到写入器
        for page in reader.pages:
            writer.add_page(page)
        
        # 更新元数据
        writer.metadata = new_metadata
        
        # 将更新后的PDF保存到新文件
        with open(save_path, 'wb') as outfile:
            writer.write(outfile)

def modify_word_metadata(file_path, new_metadata, save_path):
    """
    修改Word文档的元数据并保存为新文件。
    """
    # 首先复制文件到新位置
    shutil.copy(file_path, save_path)
    
    # 修改新文件的元数据
    doc = Document(save_path)
    prop = doc.core_properties
    for key, value in new_metadata.items():
        if hasattr(prop, key):
            setattr(prop, key, value)
    
    # 保存更改
    doc.save(save_path)