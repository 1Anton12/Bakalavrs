from fpdf import FPDF
import os
import glob

class OrderPDF(FPDF):
    def header(self):
        font_name = 'Unicode' if 'Unicode' in self.fonts else 'Arial'
        self.set_fill_color(61, 112, 179)
        self.rect(0, 0, self.w, 22, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font(font_name, 'B', 14)
        self.cell(0, 10, 'Exhibition Booth Order Summary', 0, 1, 'C')
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def find_unicode_font():
    if os.name == 'nt':
        search_dirs = [os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')]
    else:
        search_dirs = ['/usr/share/fonts', '/usr/local/share/fonts', os.path.expanduser('~/.fonts')]
    names = ['DejaVuSans', 'DejaVuSansCondensed', 'Arial', 'LiberationSans', 'FreeSans']
    for folder in search_dirs:
        for name in names:
            for ext in ['.ttf', '.TTF', '.otf', '.OTF']:
                path = os.path.join(folder, name + ext)
                if os.path.exists(path):
                    return path
        for ext in ['*.ttf', '*.TTF', '*.otf', '*.OTF']:
            for path in glob.glob(os.path.join(folder, '**', ext), recursive=True):
                lower = os.path.basename(path).lower()
                if any(n.lower() in lower for n in names):
                    return path
    return None


def draw_booth_diagram(pdf, length, width):
    max_box_width = 110
    max_box_height = 70
    scale = min(max_box_width / length, max_box_height / width, 1.0)
    box_w = length * scale
    box_h = width * scale
    x = pdf.w - pdf.r_margin - max_box_width
    y = pdf.get_y()

    pdf.set_fill_color(245, 247, 255)
    pdf.rect(x - 4, y - 4, max_box_width + 8, max_box_height + 18, 'F')
    pdf.set_draw_color(61, 112, 179)
    pdf.set_fill_color(220, 230, 250)
    pdf.rect(x + (max_box_width - box_w) / 2, y + (max_box_height - box_h) / 2, box_w, box_h, 'DF')
    pdf.set_draw_color(45, 88, 147)
    pdf.rect(x + (max_box_width - box_w) / 2, y + (max_box_height - box_h) / 2, box_w, box_h)

    pdf.set_xy(x, y + max_box_height + 4)
    pdf.set_font(pdf.font_family, 'B', 9)
    pdf.cell(max_box_width, 5, 'Approximate top view', 0, 2, 'C')
    pdf.set_font(pdf.font_family, '', 9)
    pdf.cell(max_box_width, 4, f'{length:.2f}m x {width:.2f}m', 0, 0, 'C')


def draw_section_title(pdf, title):
    pdf.set_fill_color(230, 235, 250)
    pdf.set_text_color(36, 60, 102)
    pdf.set_font(pdf.font_family, 'B', 12)
    pdf.cell(0, 8, title, 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)


def add_bullet_list(pdf, lines):
    pdf.set_font(pdf.font_family, '', 11)
    for line in lines:
        pdf.set_x(pdf.l_margin + 5)
        pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 5, 6, f'- {line}')


def generate_order_pdf(order_data, filename="order_summary.pdf"):
    pdf = OrderPDF()
    font_path = find_unicode_font()
    if font_path:
        pdf.add_font('Unicode', '', font_path)
        pdf.add_font('Unicode', 'B', font_path)
        font_name = 'Unicode'
    else:
        font_name = 'Arial'

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_font(font_name, size=11)

    pdf.set_font(font_name, 'B', 11)
    pdf.set_fill_color(241, 248, 255)
    pdf.rect(pdf.l_margin, pdf.get_y(), pdf.w - pdf.l_margin - pdf.r_margin, 24, 'F')
    pdf.set_xy(pdf.l_margin + 2, pdf.get_y() + 3)
    pdf.set_text_color(36, 60, 102)
    pdf.cell(0, 6, f"Order ID: {order_data.get('order_id', 'N/A')}", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Date: {order_data.get('date', 'N/A')}", 0, 1)
    pdf.ln(4)

    start_y = pdf.get_y()
    draw_booth_diagram(pdf, float(order_data['length']), float(order_data['width']))
    pdf.set_xy(pdf.l_margin, start_y)

    draw_section_title(pdf, 'Booth specifications')
    add_bullet_list(pdf, [
        f"Dimensions: {order_data['length']}m x {order_data['width']}m",
        f"Area: {order_data['length'] * order_data['width']:.2f} sq.m",
        f"Construction: {order_data['construction_name']}"
    ])
    pdf.ln(3)

    draw_section_title(pdf, 'Finishing')
    finishing_text = order_data.get('finishing_names', [])
    add_bullet_list(pdf, finishing_text if finishing_text else ['None'])
    pdf.ln(3)

    draw_section_title(pdf, 'Materials')
    materials_text = order_data.get('materials_names', [])
    add_bullet_list(pdf, materials_text if materials_text else ['None'])
    pdf.ln(3)

    draw_section_title(pdf, 'Equipment')
    equipment_text = order_data.get('equipment_names', [])
    add_bullet_list(pdf, equipment_text if equipment_text else ['None'])
    pdf.ln(3)

    draw_section_title(pdf, 'Services')
    services_text = order_data.get('services_names', [])
    add_bullet_list(pdf, services_text if services_text else ['None'])
    pdf.ln(6)

    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(36, 60, 102)
    pdf.set_font(font_name, 'B', 14)
    total_box_width = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.cell(total_box_width, 14, f"TOTAL PRICE: {order_data['total_price']:.2f} EUR", 0, 1, 'C', fill=True)

    pdf.set_text_color(100, 100, 100)
    pdf.set_font(font_name, '', 9)
    pdf.ln(4)
    pdf.multi_cell(0, 5, 'The illustration above is approximate and shows a simple top view of the booth. Final layout depends on the selected plan and available exhibition space.', 0, 'L')

    pdf.output(filename)
    return filename
