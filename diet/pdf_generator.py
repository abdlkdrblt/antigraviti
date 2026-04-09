import os
from io import BytesIO
from decimal import Decimal

from django.conf import settings
from django.contrib.staticfiles import finders

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, HRFlowable, PageBreak, Flowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, Rect, Group, String, Circle

def turkish_upper(text):
    if not isinstance(text, str):
        return text
    return text.replace('i', 'İ').replace('ı', 'I').upper()

class DonutChart(Flowable):
    def __init__(self, data, labels, colors_list, total_cal, page_bg):
        Flowable.__init__(self)
        self.data = data
        self.labels = labels
        self.colors_list = colors_list
        self.total_cal = total_cal
        self.page_bg = page_bg
        self.width = 17.6 * cm
        self.height = 5 * cm

    def draw(self):
        d = Drawing(self.width, self.height)
        pc = Pie()
        pc.x, pc.y = 0.5 * cm, 0.5 * cm
        pc.width, pc.height = 4 * cm, 4 * cm
        pc.data = self.data
        pc.slices.strokeWidth = 0.5
        for i, color in enumerate(self.colors_list):
            pc.slices[i].fillColor = color
        d.add(pc)
        d.add(Circle(pc.x + pc.width/2, pc.y + pc.height/2, 1.2*cm, fillColor=self.page_bg, strokeColor=colors.HexColor("#f1f5f9"), strokeWidth=0.5))
        d.add(String(pc.x + pc.width/2, pc.y + pc.height/2 + 0.1*cm, f"{int(self.total_cal)}", fontName='DejaVu-Bold', fontSize=15, fillColor=colors.HexColor("#0f172a"), textAnchor='middle'))
        d.add(String(pc.x + pc.width/2, pc.y + pc.height/2 - 0.3*cm, "TOPLAM KCAL", fontName='DejaVu', fontSize=6, fillColor=colors.HexColor("#94a3b8"), textAnchor='middle'))
        
        # Lejantı sağa daha zarif yerleştir
        for i, (label, color) in enumerate(zip(self.labels, self.colors_list)):
            y = 3.5*cm - (i * 0.7*cm)
            d.add(Circle(5.2*cm, y+0.15*cm, 0.12*cm, fillColor=color, strokeColor=None))
            d.add(String(5.6*cm, y+0.08*cm, turkish_upper(label), fontName='DejaVu', fontSize=8, fillColor=colors.HexColor("#475569")))
        d.drawOn(self.canv, 0, 0)

class ProgressBar(Flowable):
    def __init__(self, current, target, label, unit, color):
        Flowable.__init__(self)
        self.current, self.target = float(current), float(target) if target > 0 else 1
        self.label, self.unit, self.color = label, unit, color
        self.width, self.height = 7 * cm, 1 * cm

    def draw(self):
        # Üst metin alanı: Etiket solda, Değer sağda (Hedef silindi)
        self.canv.setFont("DejaVu-Bold", 7.5)
        self.canv.setFillColor(colors.HexColor("#334155"))
        self.canv.drawString(0, 0.65*cm, turkish_upper(self.label))
        
        self.canv.setFont("DejaVu-Bold", 8)
        self.canv.setFillColor(self.color)
        self.canv.drawRightString(self.width, 0.65*cm, f"{int(self.current)} {self.unit}")
        
        # Arka plan çubuğu (Daha ince ve modern)
        self.canv.setFillColor(colors.HexColor("#f1f5f9"))
        self.canv.roundRect(0, 0.25*cm, self.width, 0.12*cm, 0.06*cm, fill=1, stroke=0)
        
        # Doluluk çubuğu
        fill_w = (self.current / self.target) * self.width
        self.canv.setFillColor(self.color)
        # Eğer hedefi aştıysa çubuğu taşırmıyoruz
        self.canv.roundRect(0, 0.25*cm, min(fill_w, self.width), 0.12*cm, 0.06*cm, fill=1, stroke=0)

class DietPDFGenerator:
    def __init__(self, diet_plan):
        self.diet_plan = diet_plan
        from .models import DietitianProfile
        self.profile = DietitianProfile.objects.first()
        self.colors = {
            "primary": colors.HexColor("#1A3C34"), "accent": colors.HexColor("#C5A059"),
            "bg_page": colors.HexColor("#F9FBF9"), "text": colors.HexColor("#2d3748"),
            "text_muted": colors.HexColor("#718096"), "border": colors.HexColor("#edf2f7"),
            "cho": colors.HexColor("#1A3C34"), "prot": colors.HexColor("#C5A059"), "fat": colors.HexColor("#4a5568"),
        }
        self._register_fonts()
        self.styles = self._get_styles()

    def _register_fonts(self):
        f_reg = finders.find("fonts/DejaVuSans.ttf") or os.path.join(settings.BASE_DIR, "static/fonts/DejaVuSans.ttf")
        f_bold = finders.find("fonts/DejaVuSans-Bold.ttf") or os.path.join(settings.BASE_DIR, "static/fonts/DejaVuSans-Bold.ttf")
        pdfmetrics.registerFont(TTFont("DejaVu", f_reg))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", f_bold))

    def _get_styles(self):
        styles = getSampleStyleSheet()
        # Ünvan için büyük punto (Koyu Yeşim), İsim için küçük punto (Altın)
        styles.add(ParagraphStyle(name='Clinic_Name', fontName='DejaVu-Bold', fontSize=26, textColor=self.colors["primary"], leading=32))
        styles.add(ParagraphStyle(name='Clinic_Tagline', fontName='DejaVu', fontSize=12, textColor=self.colors["accent"], letterSpacing=1, leading=16))
        styles.add(ParagraphStyle(name='Meal_Header', fontName='DejaVu-Bold', fontSize=14, textColor=self.colors["primary"], leading=18, spaceAfter=8))
        styles.add(ParagraphStyle(name='Card_Title', fontName='DejaVu-Bold', fontSize=10, textColor=self.colors["primary"], leading=12))
        styles.add(ParagraphStyle(name='Card_Text', fontName='DejaVu', fontSize=8.5, textColor=self.colors["text"], leading=11))
        styles.add(ParagraphStyle(name='Instruction_Text', fontName='DejaVu', fontSize=9, textColor=self.colors["text"], leading=14, bulletFontName='DejaVu-Bold', bulletFontSize=8))
        return styles

    def _safe_image(self, path, width=3*cm, max_h=None):
        if not path or not os.path.exists(path): return None
        try:
            img = Image(path)
            aspect = img.imageHeight / img.imageWidth
            img.drawWidth = width
            img.drawHeight = width * aspect
            if max_h and img.drawHeight > max_h:
                ratio = max_h / img.drawHeight
                img.drawHeight, img.drawWidth = max_h, img.drawWidth * ratio
            return img
        except: return None

    def _draw_background(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(self.colors["bg_page"])
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        # İnstagram Link Düzenlemesi (Vurgulanmış & Tıklanabilir Hissiyatı)
        footer_text = "İnstagram Sayfamı Keşfet"
        footer_url = "https://www.instagram.com/diyetisyenaylinbalkan"
        
        # Yazı Stili (DejaVu-Bold ve Altın Vurgu)
        canvas.setFont("DejaVu-Bold", 7.5)
        canvas.setFillColor(self.colors["accent"])
        canvas.drawCentredString(A4[0]/2, 1.2*cm, footer_text)
        
        # Alt Çizgi (Link olduğu daha net anlaşılsın)
        t_width = canvas.stringWidth(footer_text, "DejaVu-Bold", 7.5)
        canvas.setStrokeColor(self.colors["accent"])
        canvas.setLineWidth(0.5)
        canvas.line(A4[0]/2 - t_width/2, 1.14*cm, A4[0]/2 + t_width/2, 1.14*cm)
        
        # Link alanı tanımlaması
        canvas.linkURL(footer_url, (A4[0]/2 - t_width/2, 0.9*cm, A4[0]/2 + t_width/2, 1.6*cm), relative=0)
        
        canvas.setFont("DejaVu", 7.5); canvas.setFillColor(self.colors["text_muted"])
        canvas.drawString(1.7*cm, 1.2*cm, f"Sayfa {doc.page}")
        canvas.restoreState()

    def _build_recipe_card(self, r):
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, KeepTogether
        from reportlab.lib import colors
        from reportlab.lib.units import cm

        img = self._safe_image(r.image.path if r.image else None, width=6.5*cm, max_h=5*cm) or "📷"
        instrs = [Paragraph(line.strip(), self.styles['Instruction_Text'], bulletText="•") for line in (r.instructions or "").split(".") if line.strip()]
        
        ingredients_list = []
        for ing in r.ingredients.all():
            ingredients_list.append(Paragraph(f"• {ing.name}", self.styles['Card_Text']))

        left_col = [img, Spacer(1, 12)]
        if ingredients_list:
            left_col.append(Paragraph("MALZEMELER", self.styles['Card_Title']))
            left_col.extend(ingredients_list)

        right_col = [
            Paragraph(turkish_upper(r.name), self.styles['Clinic_Name']), 
            Spacer(1, 8),
        ]
        
        if instrs:
            right_col.append(Paragraph("HAZIRLANIŞ", self.styles['Card_Title']))
            right_col.extend(instrs)
            right_col.append(Spacer(1, 10))

        if r.youtube_link:
            right_col.append(Paragraph(f"<a href='{r.youtube_link}'><b>[ ▶ Tarifimi İzle ]</b></a>", self.styles['Card_Title']))

        r_content = [ [left_col, right_col] ]
        r_card = Table(r_content, colWidths=[7*cm, 10.1*cm])
        r_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white), 
            ('VALIGN', (0,0), (-1,-1), 'TOP'), 
            ('LEFTPADDING', (0,0), (-1,-1), 10), 
            ('RIGHTPADDING', (0,0), (-1,-1), 10), 
            ('TOPPADDING', (0,0), (-1,-1), 10), 
            ('BOTTOMPADDING', (0,0), (-1,-1), 10), 
            ('BOX', (0,0), (-1,-1), 0.5, self.colors["border"]), 
            ('ROUNDEDCORNERS', [12, 12, 12, 12])
        ]))
        return KeepTogether(r_card)

    def generate(self):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm,
            topMargin=1.5*cm, bottomMargin=2.5*cm, allowSplitting=1
        )
        elements = []
        
        # --- 1. HEADER ---
        d_name = self.profile.name if self.profile else "Aylin Balkan"
        d_title = turkish_upper(self.profile.title if self.profile else "UZMAN DİYETİSYEN")
        logo = self._safe_image(self.profile.logo.path if self.profile and self.profile.logo else None, width=3.5*cm)
        # Önce Ünvan (BÜYÜK), sonra İsim (küçük)
        h_table = Table([[ [Paragraph(d_title, self.styles['Clinic_Name']), Paragraph(d_name, self.styles['Clinic_Tagline'])], logo ]], colWidths=[13*cm, 4.6*cm])
        h_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
        elements.append(h_table); elements.append(Spacer(1, 15))
        
        # --- ÇAĞDAŞ DANIŞAN KARTI (MINIMALIST LUXURY) ---
        p = self.diet_plan.patient
        if p:
            # Temiz Renk Paleti
            ACCENT = self.colors["primary"] # Orman Yeşili
            GOLD = self.colors["accent"]    # Altın
            BG = colors.white
            TEXT = self.colors["text"]
            MUTED = self.colors["text_muted"]
            
            gen_text = "Erkek" if p.gender == 'M' else "Kadın"
            
            # Sol Taraf: İsim ve Temel İstatistikler (Hiyerarşik Yapı)
            p_name_info = f"""
            <font color='{ACCENT}' size='14'><b>{turkish_upper(p.first_name)} {turkish_upper(p.last_name)}</b></font><br/>
            <font color='{GOLD}' size='8'>DANIŞAN PROFİLİ</font>
            """
            
            p_stats_grid = f"""
            <font color='{MUTED}' size='7'>BOY:</font> <font color='{TEXT}' size='8'><b>{p.height} cm</b></font>  |  
            <font color='{MUTED}' size='7'>KİLO:</font> <font color='{TEXT}' size='8'><b>{float(p.weight):g} kg</b></font>  |  
            <font color='{MUTED}' size='7'>YAŞ:</font> <font color='{TEXT}' size='8'><b>{p.age}</b></font>  |  
            <font color='{MUTED}' size='7'>CİNSİYET:</font> <font color='{TEXT}' size='8'><b>{gen_text}</b></font>
            """
            
            # Sağ Taraf: Kişiye Özel Not
            p_note_html = f"<font color='{ACCENT}' size='8'><b>DANIŞAN NOTU:</b></font><br/>"
            if p.special_note:
                clean_note = p.special_note.replace('\n', '<br/>')
                p_note_html += f"<font color='{TEXT}' size='8'><i>{clean_note}</i></font>"
            else:
                p_note_html += f"<font color='{MUTED}' size='8'>Bu diyet planı size özel olarak hazırlanmıştır.</font>"

            # Kartın İçeriği (İki Sütunlu)
            p_card_content = [[ 
                [Paragraph(p_name_info, self.styles['Card_Text']), Spacer(1, 8), Paragraph(p_stats_grid, self.styles['Card_Text'])],
                Paragraph(p_note_html, self.styles['Card_Text'])
            ]]
            
            p_card = Table(p_card_content, colWidths=[9.5*cm, 8.1*cm])
            p_card.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), BG),
                ('BOX', (0,0), (-1,-1), 0.5, self.colors["border"]), # İnce gri çerçeve
                ('LINEABOVE', (0,0), (-1,0), 2, GOLD), # Üstte ince altın şerit (Contemporary Touch)
                ('ROUNDEDCORNERS', [4, 4, 4, 4]),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 15),
                ('RIGHTPADDING', (0,0), (-1,-1), 15),
                ('TOPPADDING', (0,0), (-1,-1), 15),
                ('BOTTOMPADDING', (0,0), (-1,-1), 15),
            ]))
            elements.append(p_card)
            elements.append(Spacer(1, 20))

        # --- 2. PREMIUM DASHBOARD ---
        t_cal, t_cho, t_prot, t_fat = Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")
        recipe_list = []
        from .models import ExchangeGroup
        self.item_exchanges = []
        meals = self.diet_plan.meals.all().order_by("meal_type")
        for m in meals:
            for mf in m.mealfood_set.select_related('food').prefetch_related('alternatives').all():
                if mf.food:
                    q = Decimal(str(mf.measure_value))
                    t_cal += mf.food.calories * q; t_cho += mf.food.carbohydrates * q
                    t_prot += mf.food.protein * q; t_fat += mf.food.fat * q
                
                # ALTERNATİF TARİFLERİ TOPLA (Besin altındakiler)
                from .models import Recipe
                for alt in mf.alternatives.all():
                    if isinstance(alt.item, Recipe):
                        recipe_list.append(alt.item)

            for mr in m.mealrecipe_set.select_related('recipe').prefetch_related('alternatives').all():
                r = mr.recipe; q = Decimal(str(mr.measure_value or 1))
                if r:
                    recipe_list.append(r)
                    t_cal += (r.calories or 0)*q; t_cho += (r.carbohydrates or 0)*q; t_prot += (r.protein or 0)*q; t_fat += (r.fat or 0)*q
                
                # ALTERNATİF TARİFLERİ TOPLA (Tarif altındakiler)
                from .models import Recipe
                for alt in mr.alternatives.all():
                    if isinstance(alt.item, Recipe):
                        recipe_list.append(alt.item)

        self.attached_lists = ExchangeGroup.objects.prefetch_related('items__food', 'items__recipe', 'items__unit').all()
        self.item_exchanges = []

        target_cal = float(self.diet_plan.target_calories); t_pct = self.diet_plan
        target_cho = (target_cal * (t_pct.target_carb_percent/100)) / 4
        target_prot = (target_cal * (t_pct.target_prot_percent/100)) / 4
        target_fat = (target_cal * (t_pct.target_fat_percent/100)) / 9

        # elements.append(Paragraph("HAFTALIK KLİNİK ANALİZ ÖZETİ", self.styles['Meal_Header']))
        # elements.append(HRFlowable(width="100%", thickness=0.5, color=self.colors["border"], spaceAfter=10))
        # 
        # chart = DonutChart([float(t_cho*4), float(t_prot*4), float(t_fat*9)], ["Karbonhidrat", "Protein", "Yağ"], [self.colors["cho"], self.colors["prot"], self.colors["fat"]], t_cal, self.colors["bg_page"])
        # dash_content = [[ chart, [
        #     ProgressBar(t_cal, target_cal, "Enerji Dengesi", "kcal", self.colors["primary"]), 
        #     Spacer(1, 4), 
        #     ProgressBar(t_cho, target_cho, "Karbonhidrat", "g", self.colors["cho"]), 
        #     Spacer(1, 4), 
        #     ProgressBar(t_prot, target_prot, "Protein", "g", self.colors["prot"]), 
        #     Spacer(1, 4), 
        #     ProgressBar(t_fat, target_fat, "Yağ", "g", self.colors["fat"])
        # ] ]]
        # 
        # dash_table = Table(dash_content, colWidths=[9*cm, 8.6*cm])
        # dash_table.setStyle(TableStyle([
        #     ('BACKGROUND', (0,0), (-1,-1), colors.white),
        #     ('BOX', (0,0), (-1,-1), 0.7, self.colors["border"]),
        #     ('ROUNDEDCORNERS', [12, 12, 12, 12]),
        #     ('TOPPADDING', (0,0), (-1,-1), 20),
        #     ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        #     ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        #     ('LEFTPADDING', (1,0), (1,0), 15),
        # ]))
        # elements.append(dash_table); elements.append(Spacer(1, 20))

        # --- 3. MEAL TABLE STRUCTURE (SPLIT-FRIENDLY) ---
        for m in meals:
            # Her öğün için TEK ana tablo oluştur
            time_text = f" <font color='#C5A059' size='11'>[  {m.meal_time} ]</font>" if m.meal_time else ""
            header_text = f"{turkish_upper(m.get_meal_type_display())} {time_text}"
            meal_data = [[ Paragraph(header_text, self.styles['Meal_Header']) ]]
            
            # Öğün altındaki tüm besinleri ve tarifleri satır olarak ekle
            # Öğün altındaki tüm besinleri ve tarifleri satır olarak ekle
            for mf in m.mealfood_set.select_related('measure_unit', 'food', 'food__measure_unit').prefetch_related('alternatives', 'alternatives__measure_unit').all():
                q = Decimal(str(mf.measure_value))
                icon = "📦"
                
                # 'Birim' -> 'Değişim' dönüşümü ve porsiyon notu
                val_g = float(mf.measure_value)
                unit_label = "Ölçü" if val_g >= 1 else (mf.measure_unit.name if mf.measure_unit else 'Birim')
                p_text = f"{val_g:g} {unit_label}"
                
                # 1 Porsiyon Referans Bilgisi
                ref_info = ""
                if mf.food:
                    f_ref_val = float(mf.food.measure_value)
                    f_ref_unit = mf.food.measure_unit.name if mf.food.measure_unit else "Birim"
                    # Eğer miktar 1 ise gösterme, sadece birimi yaz
                    f_val_str = f"{f_ref_val:g} " if f_ref_val != 1.0 else ""
                    ref_info = f" <font color='#6b7280' size='8'>(1 Porsiyonu: {f_val_str}{f_ref_unit})</font>"

                multiplier_note = ""
                if val_g > 1:
                    multiplier_note = f"<br/><br/><font color='#1A3C34'><b>HATIRLATMA:</b> <i>{val_g:g} ölçü porsiyon miktarının {val_g:g} katıdır.</i></font>"

                f_name = mf.food.name if mf.food else "Besin"
                cals = (mf.food.calories * q) if mf.food else 0
                
                # ALTERNATİFLERİ TOPLA
                alts = list(mf.alternatives.all())
                alt_text = ""
                if alts:
                    alt_names = []
                    for a in alts:
                        obj = a.item
                        if obj:
                            a_val = float(a.measure_value)
                            a_qty = f"{a_val:g}"
                            a_unit = "Birim" if a_val >= 1 else (a.measure_unit.name if a.measure_unit else "Birim")
                            
                            # Alternatifin 1 porsiyon referansını da ekle
                            a_ref_info = ""
                            if hasattr(obj, 'measure_value') and hasattr(obj, 'measure_unit'):
                                r_val = float(obj.measure_value)
                                r_unit = obj.measure_unit.name if obj.measure_unit else "Birim"
                                r_val_str = f"{r_val:g} " if r_val != 1.0 else ""
                                a_ref_info = f" [1 Pors. {r_val_str}{r_unit}]"
                                
                            alt_names.append(f"{obj.name}{a_ref_info} ({a_qty} {a_unit})")
                    if alt_names:
                        alt_text = f"<br/><br/><font color='#10b981'><b>Alternatifler:</b></font> {', '.join(alt_names)}"

                # --- 0 Kalori Mantığı ---
                if cals == 0:
                    description_paras = [ Paragraph(f"<b>{f_name}</b>", self.styles['Card_Title']) ]
                    if alt_text: description_paras.append(Paragraph(alt_text, self.styles['Card_Text']))
                    if multiplier_note: description_paras.append(Paragraph(multiplier_note, self.styles['Card_Text']))
                else:
                    description_paras = [
                        Paragraph(f"<b>{f_name}</b>{ref_info}", self.styles['Card_Title']), 
                        Paragraph(f"{alt_text}{multiplier_note}", self.styles['Card_Text']) if alt_text or multiplier_note else Spacer(1, 0)
                    ]

                inner_card = Table([[ description_paras ]], colWidths=[17.1*cm])
                inner_card.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.white), ('BOX', (0,0), (-1,-1), 0.3, self.colors["border"]), ('ROUNDEDCORNERS', [8, 8, 8, 8]), ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 12)]))
                meal_data.append([inner_card])

            for mr in m.mealrecipe_set.select_related('recipe', 'measure_unit', 'recipe__measure_unit').prefetch_related('alternatives', 'alternatives__measure_unit').all():
                r = mr.recipe; q = Decimal(str(mr.measure_value or 1))
                icon = "🥗"
                
                # 'Porsiyon' -> 'Değişim' dönüşümü ve porsiyon notu
                val_g = float(mr.measure_value or 1)
                unit_label = "Değişim" if val_g >= 1 else (mr.measure_unit.name if mr.measure_unit else 'Porsiyon')
                p_text = f"{val_g:g} {unit_label}"
                
                # 1 Porsiyon Referans Bilgisi (Tarif için)
                ref_info = ""
                if r:
                    r_ref_val = float(r.measure_value)
                    r_ref_unit = r.measure_unit.name if r.measure_unit else "Porsiyon"
                    # Eğer miktar 1 ise gösterme, sadece birimi yaz
                    r_val_str = f"{r_ref_val:g} " if r_ref_val != 1.0 else ""
                    ref_info = f" <font color='#6b7280' size='8'>(1 Porsiyonu: {r_val_str}{r_ref_unit})</font>"
                
                multiplier_note = ""
                if val_g > 1:
                    multiplier_note = f"<br/><br/><font color='#1A3C34'><b>HATIRLATMA:</b> <i>{val_g:g} değişim porsiyon miktarının {val_g:g} katıdır.</i></font>"

                # ALTERNATİFLERİ TOPLA
                alts = list(mr.alternatives.all())
                alt_text = ""
                if alts:
                    alt_names = []
                    for a in alts:
                        obj = a.item
                        if obj:
                            a_val = float(a.measure_value)
                            a_qty = f"{a_val:g}"
                            a_unit = "Değişim" if a_val >= 1 else (a.measure_unit.name if a.measure_unit else "Birim")
                            
                            # Alternatifin 1 porsiyon referansını da ekle (Recipe ise 'Porsiyon' varsayıyoruz)
                            a_ref_info = ""
                            if hasattr(obj, 'measure_value') and hasattr(obj, 'measure_unit'):
                                r_val = float(obj.measure_value)
                                r_unit = obj.measure_unit.name if obj.measure_unit else "Birim"
                                r_val_str = f"{r_val:g} " if r_val != 1.0 else ""
                                a_ref_info = f" [1 Pors. {r_val_str}{r_unit}]"
                            else:
                                # Tarifler için referans miktar genelde porsiyondur
                                a_ref_info = f" [1 Porsiyon]"

                            alt_names.append(f"{obj.name}{a_ref_info} ({a_qty} {a_unit})")
                    if alt_names:
                        alt_text = f"<br/><br/><font color='#10b981'><b>Alternatifler:</b></font> {', '.join(alt_names)}"

                r_cals = (r.calories or 0)*q if r else 0
                
                # --- 0 Kalori Mantığı (Tarifler İçin) ---
                if r_cals == 0:
                    description_paras = [ Paragraph(f"<b>{r.name if r else 'Tarif'}</b>", self.styles['Card_Title']) ]
                    if alt_text: description_paras.append(Paragraph(alt_text, self.styles['Card_Text']))
                    if multiplier_note: description_paras.append(Paragraph(multiplier_note, self.styles['Card_Text']))
                else:
                    description_paras = [
                        Paragraph(f"<b>{r.name if r else 'Tarif'}</b>{ref_info}", self.styles['Card_Title']), 
                        Paragraph(f"{alt_text}{multiplier_note}", self.styles['Card_Text']) if alt_text or multiplier_note else Spacer(1, 0)
                    ]

                inner_card = Table([[ description_paras ]], colWidths=[17.1*cm])
                inner_card.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f7fafc")), ('BOX', (0,0), (-1,-1), 0.3, self.colors["accent"]), ('ROUNDEDCORNERS', [8, 8, 8, 8]), ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 12)]))
                meal_data.append([inner_card])

            if len(meal_data) > 1:
                main_meal_table = Table(meal_data, colWidths=[17.6*cm], splitByRow=1)
                main_meal_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('NOSPLIT', (0,0), (0,1)), # Başlık ve ilk öğeyi asla ayırma
                ]))
                elements.append(main_meal_table)
                if m.notes:
                    elements.append(Paragraph(f"<i>Not: {m.notes}</i>", self.styles['Card_Text']))
                elements.append(Spacer(1, 5))

        # --- 4. RECIPE BOX (KEEP TOGETHER - NO HARD PAGE BREAK) ---
        if recipe_list:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Diyet Listendeki Tarifler", self.styles['Meal_Header']))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=self.colors["border"], spaceAfter=10))
            
            seen = set()
            for r in recipe_list:
                if r.id in seen: continue
                seen.add(r.id)
                
                r_card = self._build_recipe_card(r)
                elements.append(r_card)
                elements.append(Spacer(1, 12))

        # --- 6. DIETITIAN RECOMMENDATIONS (DİYETİSYEN ÖNERİLERİ) ---
        recs = self.diet_plan.recommendations.all()
        if recs:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("DİYETİSYEN ÖNERİLERİ VE TAVSİYELER", self.styles['Clinic_Name']))
            elements.append(Paragraph("SÜRECİNİZİ DESTEKLEYECEK ÖZEL KLİNİK TAVSİYELERİMİZ", self.styles['Clinic_Tagline']))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=self.colors["border"], spaceAfter=10))
            elements.append(Spacer(1, 10))

            for r in recs:
                rec_card = Table([
                    [Paragraph(turkish_upper(r.title), self.styles['Card_Title'])],
                    [Paragraph(r.content, self.styles['Instruction_Text'])]
                ], colWidths=[17.6*cm])
                rec_card.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.white),
                    ('BOX', (0,0), (-1,-1), 0.5, self.colors["accent"]),
                    ('ROUNDEDCORNERS', [10, 10, 10, 10]),
                    ('TOPPADDING', (0,0), (-1,0), 12),    # Başlık üst boşluğu
                    ('BOTTOMPADDING', (0,0), (-1,0), 2),     # Başlık-İçerik arası (üstten)
                    ('TOPPADDING', (0,1), (-1,1), 2),        # Başlık-İçerik arası (alttan)
                    ('BOTTOMPADDING', (0,1), (-1,1), 12), # İçerik alt boşluğu
                    ('LEFTPADDING', (0,0), (-1,-1), 15),
                    ('RIGHTPADDING', (0,0), (-1,-1), 15),
                ]))
                elements.append(KeepTogether(rec_card))
                elements.append(Spacer(1, 12))

        # --- 7. GENİŞLETİLMİŞ ALIŞVERİŞ LİSTESİ (REFACTORED & AT THE END) ---
        # from .models import Recipe, Food
        # shop_foods = {} # (name, unit): {name, qty, unit, is_alt}
        # shop_recipes = {} # r_id: {obj, is_alt, multiplier}
        # 
        # for m in meals:
        #     # Foods Analysis
        #     for mf in m.mealfood_set.all():
        #         if mf.food:
        #             u = mf.measure_unit.name if mf.measure_unit else "Birim"
        #             key = (mf.food.name, u)
        #             if key not in shop_foods: shop_foods[key] = {'name': mf.food.name, 'qty': Decimal("0"), 'unit': u, 'is_alt': False}
        #             shop_foods[key]['qty'] += Decimal(str(mf.measure_value))
        #         for alt in mf.alternatives.all():
        #             it = alt.item
        #             u = alt.measure_unit.name if alt.measure_unit else "Birim"
        #             if isinstance(it, Food):
        #                 key = (it.name, u)
        #                 if key not in shop_foods: shop_foods[key] = {'name': it.name, 'qty': Decimal("0"), 'unit': u, 'is_alt': True}
        #                 shop_foods[key]['qty'] += Decimal(str(alt.measure_value))
        #             elif isinstance(it, Recipe):
        #                 if it.id not in shop_recipes: shop_recipes[it.id] = {'obj': it, 'is_alt': True, 'mult': Decimal("0")}
        #                 shop_recipes[it.id]['mult'] += Decimal(str(alt.measure_value))
        # 
        #     # Recipes Analysis
        #     for mr in m.mealrecipe_set.all():
        #         if mr.recipe:
        #             rid = mr.recipe.id
        #             if rid not in shop_recipes: shop_recipes[rid] = {'obj': mr.recipe, 'is_alt': False, 'mult': Decimal("0")}
        #             shop_recipes[rid]['mult'] += Decimal(str(mr.measure_value or 1))
        #         for alt in mr.alternatives.all():
        #             it = alt.item
        #             if isinstance(it, Recipe):
        #                 if it.id not in shop_recipes: shop_recipes[it.id] = {'obj': it, 'is_alt': True, 'mult': Decimal("0")}
        #                 shop_recipes[it.id]['mult'] += Decimal(str(alt.measure_value))
        #             elif isinstance(it, Food):
        #                 u = alt.measure_unit.name if alt.measure_unit else "Birim"
        #                 key = (it.name, u)
        #                 if key not in shop_foods: shop_foods[key] = {'name': it.name, 'qty': Decimal("0"), 'unit': u, 'is_alt': True}
        #                 shop_foods[key]['qty'] += Decimal(str(alt.measure_value))
        # 
        # if shop_foods or shop_recipes:
        #     elements.append(Spacer(1, 20))
        #     elements.append(HRFlowable(width="100%", thickness=1, color=self.colors["accent"], spaceAfter=20))
        #     elements.append(Paragraph("HAFTALIK ALIŞVERİŞ REHBERİ", self.styles['Clinic_Name']))
        #     elements.append(Paragraph("PLANINIZA GÖRE ÖZELLEŞTİRİLMİŞ MARKET LİSTESİ", self.styles['Clinic_Tagline']))
        #     elements.append(HRFlowable(width="100%", thickness=0.5, color=self.colors["border"], spaceAfter=15))
        #     
        #     # --- BESİNLER GRUBU ---
        #     if shop_foods:
        #         elements.append(Paragraph("TEMEL BESİNLER VE ATIŞTIRMALIKLAR", self.styles['Meal_Header']))
        #         food_rows = []
        #         sorted_foods = sorted(shop_foods.values(), key=lambda x: x['name'])
        #         for f_item in sorted_foods:
        #             star = "*" if f_item['is_alt'] else ""
        #             food_rows.append(Paragraph(f"☐ <b>{f_item['name']}</b>{star}", self.styles['Card_Text']))
        #         
        #         # Sütunlu tabloya böl (3 sütun)
        #         cols = 3
        #         grid_data = [food_rows[i:i+cols] for i in range(0, len(food_rows), cols)]
        #         # Eksik hücreleri doldur
        #         for row in grid_data: 
        #             while len(row) < cols: row.append("")
        #         
        #         f_table = Table(grid_data, colWidths=[5.8*cm]*cols)
        #         f_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'), ('LEFTPADDING',(0,0),(-1,-1),5), ('TOPPADDING',(0,0),(-1,-1),5)]))
        #         elements.append(f_table)
        #         elements.append(Spacer(1, 20))
        # 
        #     # --- TARİFLER VE İÇERİKLERİ ---
        #     if shop_recipes:
        #         elements.append(Paragraph("TARİF İÇERİKLERİ VE ÖZEL KARIŞIMLAR", self.styles['Meal_Header']))
        #         for r_id, r_data in shop_recipes.items():
        #             r_obj = r_data['obj']
        #             star = "*" if r_data['is_alt'] else ""
        #             mult = float(r_data['mult'])
        #             
        #             r_header = Paragraph(f"<b>{r_obj.name.upper()}</b>{star} <font size='8' color='#64748b'>({mult:g} Değişim için)</font>", self.styles['Card_Title'])
        #             
        #             ing_texts = []
        #             for ing in r_obj.ingredients.all():
        #                 i_name = ing.name
        #                 ing_texts.append(Paragraph(f"• {i_name}", self.styles['Card_Text']))
        #             
        #             # Tarif kartı gibi paketle
        #             r_ing_table = Table([[ [r_header, Spacer(1, 4)] + ing_texts ]], colWidths=[17.6*cm])
        #             r_ing_table.setStyle(TableStyle([
        #                 ('BACKGROUND', (0,0), (-1,-1), colors.white),
        #                 ('BOX', (0,0), (-1,-1), 0.5, self.colors["border"]),
        #                 ('LEFTBORDER', (0,0), (0,0), 3, self.colors["accent"]),
        #                 ('TOPPADDING', (0,0), (-1,-1), 10),
        #                 ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        #                 ('LEFTPADDING', (0,0), (-1,-1), 15),
        #             ]))
        #             elements.append(KeepTogether(r_ing_table))
        #             elements.append(Spacer(1, 10))
        # 
        #     elements.append(Spacer(1, 10))
        #     elements.append(Paragraph("<font size='7' color='#ef4444'>* Yıldız işareti ile belirtilenler alternatif öğün tercihleriniz için gerekli olanlardır.</font>", self.styles['Card_Text']))

        doc.build(elements, onFirstPage=self._draw_background, onLaterPages=self._draw_background)
        return buffer.getvalue()