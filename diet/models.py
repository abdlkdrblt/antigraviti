from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class DietitianProfile(models.Model):
    name = models.CharField(max_length=200, default="Diyetisyen Aylin Balkan", verbose_name="Diyetisyen Adı")
    title = models.CharField(max_length=200, default="Uzman Diyetisyen", verbose_name="Unvan")
    logo = models.ImageField(upload_to='diet/logos/', blank=True, null=True, verbose_name="Kurumsal Logo")
    website = models.URLField(blank=True, null=True, verbose_name="Web Sitesi")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="İletişim Numarası")

    class Meta:
        verbose_name = "Diyetisyen Profili"
        verbose_name_plural = "Diyetisyen Profili"

    def __str__(self):
        return self.name

class DietRecommendation(models.Model):
    title = models.CharField(max_length=200, verbose_name="Önerilen Tavsiye Başlığı")
    content = models.TextField(verbose_name="Tavsiye İçeriği")

    class Meta:
        verbose_name = "Diyetisyen Önerisi"
        verbose_name_plural = "Diyetisyen Önerileri"

    def __str__(self):
        return self.title

class MeasureUnit(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Ölçü Birimi (Örn: Dilim, Adet, Kase)")

    class Meta:
        verbose_name = "Ölçü Birimi"
        verbose_name_plural = "Ölçü Birimleri"

    def __str__(self):
        return self.name

class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Erkek'), ('F', 'Kadın')]
    first_name = models.CharField(max_length=100, verbose_name="Ad")
    last_name = models.CharField(max_length=100, verbose_name="Soyad")
    height = models.PositiveIntegerField(verbose_name="Boy (cm)")
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Kilo (kg)")
    age = models.PositiveIntegerField(verbose_name="Yaş")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Cinsiyet")
    activity_level = models.DecimalField(max_digits=3, decimal_places=2, default=1.2, verbose_name="Aktivite Katsayısı (1.2-1.9)")
    special_note = models.TextField(blank=True, null=True, verbose_name="Danışana Özel Not")
    
    class Meta:
        verbose_name = "Danışan"
        verbose_name_plural = "Danışanlar"

    def calculate_bmr(self):
        """Harris-Benedict Eşitliği"""
        if self.gender == 'M':
            # Erkekler için BMH: 66,5 + (5 × Boy (cm)) + (13,75 × Kilo (kg)) − (6,77 × Yaş)
            return 66.5 + (5 * float(self.height)) + (13.75 * float(self.weight)) - (6.77 * self.age)
        else:
            # Kadınlar için BMH: 655,1 + (1,85 × Boy (cm)) + (9,56 × Kilo (kg)) − (4,67 × Yaş)
            return 655.1 + (1.85 * float(self.height)) + (9.56 * float(self.weight)) - (4.67 * self.age)
            
    def calculate_maintenance_calories(self):
        return self.calculate_bmr() * float(self.activity_level)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class FoodGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Grup Adı. (Örn: Süt, Et, Meyve)")
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Karbonhidrat (g)")
    protein = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Protein (g)")
    fat = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Yağ (g)")

    class Meta:
        verbose_name = "Besin Grubu (Değişim)"
        verbose_name_plural = "Besin Grupları"

    def __str__(self):
        return self.name

class Food(models.Model):
    food_group = models.ForeignKey(FoodGroup, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Besin Grubu")
    name = models.CharField(max_length=200, verbose_name="Besin Adı")
    measure_value = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="Ölçü Miktarı")
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ölçü Birimi")
    calories = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Kalori (kcal)")
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Karbonhidrat (g)")
    protein = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Protein (g)")
    fat = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Yağ (g/porsiyon)")

    class Meta:
        verbose_name = "Besin"
        verbose_name_plural = "Besinler"
        ordering = ['name']

    def __str__(self):
        unit_name = self.measure_unit.name if self.measure_unit else "Birim Yok"
        return f"{self.name} ({float(self.measure_value):g} {unit_name})"

class ExchangeGroup(models.Model):
    name = models.CharField(max_length=200, verbose_name="Değişim Grubu Adı (Örn: Ekmek Grubu)")
    description = models.TextField(blank=True, null=True, verbose_name="Grup Açıklaması")

    class Meta:
        verbose_name = "Değişim Grubu"
        verbose_name_plural = "Değişim Grupları"

    def __str__(self):
        return self.name

class ExchangeItem(models.Model):
    group = models.ForeignKey(ExchangeGroup, on_delete=models.CASCADE, related_name="items", verbose_name="Bağlı Olduğu Grup")
    
    # Senior Çözüm: Autocomplete desteği için içerik tipini doğrudan FK ile bağlıyoruz
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Besin Seçimi")
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tarif Seçimi")
    
    # Klinik Porsiyon Değeri (1 Birim Değişim Karşılığı)
    reference_quantity = models.DecimalField(max_digits=7, decimal_places=2, default=1.0, 
                                           help_text="Bu grup için '1 Değişim' karşılığı olan miktar (Örn: 100g Elma, 1 Adet Kek)",
                                           verbose_name="Referans Miktar")
    unit = models.ForeignKey('MeasureUnit', on_delete=models.SET_NULL, null=True, blank=True, 
                            verbose_name="Birim", help_text="Seçilen öğenin birimiyle otomatik eşleşir.")

    class Meta:
        verbose_name = "Grup Öğesi"
        verbose_name_plural = "Grup Öğeleri"

    def __str__(self):
        obj = self.food if self.food else (self.recipe if self.recipe else None)
        if obj:
            return f"[{self.group.name}] {obj.name}"
        return f"[{self.group.name}] Tanımsız Öğe"

    def save(self, *args, **kwargs):
        # Otomatik Birim Eşleme
        obj = self.food if self.food else self.recipe
        if obj and not self.unit:
            self.unit = getattr(obj, 'measure_unit', None)
        super().save(*args, **kwargs)

class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tarif Adı")
    food_group = models.ForeignKey(FoodGroup, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ait Olduğu Eşdeğer Grubu")
    instructions = models.TextField(verbose_name="Hazırlanış Metni")
    image = models.ImageField(upload_to='diet/recipes/', blank=True, null=True, verbose_name="Tarif Görseli")
    youtube_link = models.URLField(blank=True, null=True, verbose_name="YouTube Linki")
    calories = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Kalori (kcal)")
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Karbonhidrat (g)")
    protein = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Protein (g)")
    fat = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Yağ (g)")
    measure_value = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="Ölçü Miktarı")
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ölçü Birimi")

    class Meta:
        verbose_name = "Tarif"
        verbose_name_plural = "Tarifler"
        ordering = ['name']

    def __str__(self):
        return self.name

class RecipePortion(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="portions", verbose_name="Tarif")
    food_group = models.ForeignKey(FoodGroup, on_delete=models.CASCADE, verbose_name="Besin Grubu")
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="Porsiyon Adedi")

    class Meta:
        verbose_name = "Tarif Porsiyonu"
        verbose_name_plural = "Tarif Porsiyonları"

    def __str__(self):
        return f"{self.amount} Porsiyon {self.food_group.name}"

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients", verbose_name="Tarif")
    name = models.CharField(max_length=200, verbose_name="Besin Adı", default="Malzeme")
    measure_value = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="Ölçü Miktarı")
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ölçü Birimi")
    calories = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Kalori (kcal)")
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Karbonhidrat (g)")
    protein = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Protein (g)")
    fat = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Yağ (g)")

    class Meta:
        verbose_name = "Tarif Malzemesi"
        verbose_name_plural = "Tarif Malzemeleri"

    def __str__(self):
        unit_name = self.measure_unit.name if self.measure_unit else "Birim"
        return f"{self.measure_value} {unit_name} {self.name}"


class DietPlan(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="diet_plans", verbose_name="Danışan", null=True, blank=True)
    logo = models.ImageField(upload_to='diet/logos/', blank=True, null=True, verbose_name="Diyetisyen Logosu / Banner")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    # Hedefler
    target_calories = models.PositiveIntegerField(default=2000, verbose_name="Hedef Enerji (kcal)")
    target_carb_percent = models.PositiveIntegerField(default=50, verbose_name="Hedef CHO %")
    target_prot_percent = models.PositiveIntegerField(default=20, verbose_name="Hedef Prot %")
    target_fat_percent = models.PositiveIntegerField(default=30, verbose_name="Hedef Yağ %")
    
    recommendations = models.ManyToManyField(DietRecommendation, blank=True, verbose_name="Diyetisyen Önerileri")
    
    class Meta:
        verbose_name = "Diyet Planı"
        verbose_name_plural = "Diyet Planları"

    def __str__(self):
        return f"{self.patient} - {self.created_at.strftime('%Y-%m-%d')}"
    def save(self, *args, **kwargs):
        # Eğer özel bir logo yüklenmemişse ve bir diyetisyen profili varsa, profil logosunu varsayılan yap
        if not self.logo:
            profile = DietitianProfile.objects.first()
            if profile and profile.logo:
                self.logo = profile.logo
        super().save(*args, **kwargs)


    @property
    def target_carb_grams(self):
        return (self.target_calories * self.target_carb_percent / 100) / 4

    @property
    def target_prot_grams(self):
        return (self.target_calories * self.target_prot_percent / 100) / 4

    @property
    def target_fat_grams(self):
        return (self.target_calories * self.target_fat_percent / 100) / 9

class DietPlanTargetPortion(models.Model):
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name="target_portions", verbose_name="Diyet Planı")
    food_group = models.ForeignKey(FoodGroup, on_delete=models.CASCADE, verbose_name="Besin Grubu")
    target_amount = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Hedef Porsiyon")

    class Meta:
        verbose_name = "Diyet Hedef Porsiyonu"
        verbose_name_plural = "Diyet Hedef Porsiyonları"

    def __str__(self):
        return f"{self.food_group.name}: {self.target_amount} Porsiyon"


class Meal(models.Model):
    MEAL_CHOICES = [
        ('0_UYANINCA', 'Uyanınca Ara Öğünü'),
        ('1_KAHVALTI', 'Kahvaltı'),
        ('2_KAH_SONRASI', 'Kahvaltı Sonrası Ara Öğün'),
        ('3_OGLE_ONCESI', 'Öğle Öncesi Ara Öğün'),
        ('4_OGLE', 'Öğle Yemeği'),
        ('5_OGLE_SONRASI', 'Öğle Sonrası Ara Öğün'),
        ('6_AKSAM_ONCESI', 'Akşam Öncesi Ara Öğün'),
        ('7_AKSAM', 'Akşam Yemeği'),
        ('8_AKSAM_SONRASI', 'Akşam Sonrası Ara Öğün'),
        ('9_GECE', 'Gece Öğünü'),
    ]
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name="meals", verbose_name="Diyet Planı")
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, verbose_name="Öğün Tipi")
    meal_time = models.TimeField(null=True, blank=True, verbose_name="Öğün Saati")
    meal_image = models.ImageField(upload_to='diet/meals/', blank=True, null=True, verbose_name="Öğün Görseli (Opsiyonel)")
    notes = models.TextField(blank=True, null=True, verbose_name="Öğün Notları")

    class Meta:
        verbose_name = "Öğün"
        verbose_name_plural = "Öğünler"
        ordering = ['meal_type']

    def __str__(self):
        time_str = f" ({self.meal_time.strftime('%H:%M')})" if self.meal_time else ""
        return f"{self.diet_plan.patient} - {self.get_meal_type_display()}{time_str}"


class MealFood(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, verbose_name="Öğün")
    food = models.ForeignKey(Food, on_delete=models.CASCADE, verbose_name="Besin Özütü Seçimi", null=True, blank=True)
    measure_value = models.DecimalField(max_digits=5, decimal_places=2, default=1, verbose_name="Ölçü Miktarı")
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ölçü Birimi")

    class Meta:
        verbose_name = "Öğün Besini"
        verbose_name_plural = "Öğün Besinleri"

    def __str__(self):
        unit_name = self.measure_unit.name if self.measure_unit else "Birim"
        f_name = self.food.name if self.food else "Besin"
        return f"{self.measure_value} {unit_name} {f_name} ({self.meal})"


class MealAlternative(models.Model):
    meal_food = models.ForeignKey('MealFood', on_delete=models.CASCADE, related_name="alternatives", verbose_name="Öğün Besini", null=True, blank=True)
    meal_recipe = models.ForeignKey('MealRecipe', on_delete=models.CASCADE, related_name="alternatives", verbose_name="Öğün Tarifi", null=True, blank=True)
    
    # Generic Item Selection (Food or Recipe)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Öğe Tipi (Besin/Tarif)")
    object_id = models.PositiveIntegerField(verbose_name="Öğe ID")
    item = GenericForeignKey('content_type', 'object_id')
    
    measure_value = models.DecimalField(max_digits=5, decimal_places=2, default=1, verbose_name="Ölçü Miktarı")
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ölçü Birimi")

    class Meta:
        verbose_name = "Meal Alternatifi"
        verbose_name_plural = "Meal Alternatifleri"

    def __str__(self):
        obj_name = self.item.name if self.item else "Öğe"
        unit = self.measure_unit.name if self.measure_unit else "Birim"
        return f"+ Alternatif: {float(self.measure_value):g} {unit} {obj_name}"



class MealRecipe(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, verbose_name="Öğün")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Tarif", null=True, blank=True)
    measure_value = models.DecimalField(max_digits=5, decimal_places=2, default=1, verbose_name="Ölçü Miktarı (Çarpan)")
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ölçü Birimi")

    class Meta:
        verbose_name = "Öğün Tarifi"
        verbose_name_plural = "Öğün Tarifleri"

    def __str__(self):
        unit_name = self.measure_unit.name if self.measure_unit else "Birim"
        r_name = self.recipe.name if self.recipe else "Tarif"
        return f"{self.measure_value} {unit_name} {r_name} ({self.meal})"


