import nested_admin
from django import forms
from django.contrib import admin
from django.forms import HiddenInput
from django.utils.html import format_html

from .models import (
    FoodGroup, Food, Recipe, DietPlan, Meal,
    MealFood, MealRecipe, DietitianProfile, Patient, MeasureUnit, RecipeIngredient,
    ExchangeGroup, ExchangeItem, MealAlternative, DietRecommendation,
    RecipePortion, DietPlanTargetPortion
)


class MeasureUnitManualForm(forms.ModelForm):
    measure_unit_manual = forms.CharField(
        required=False,
        label="Ölçü Birimi",
    )

    class Meta:
        fields = "__all__"
        exclude = ["measure_unit"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "measure_unit_manual" in self.fields:
            existing_class = self.fields["measure_unit_manual"].widget.attrs.get("class", "")
            self.fields["measure_unit_manual"].widget.attrs["class"] = f"{existing_class} measure-unit-manual-field".strip()

        if (
            self.instance
            and self.instance.pk
            and hasattr(self.instance, "measure_unit")
            and self.instance.measure_unit
        ):
            self.fields["measure_unit_manual"].initial = self.instance.measure_unit.name

    def save(self, commit=True):
        instance = super().save(commit=False)
        unit_name = self.cleaned_data.get("measure_unit_manual")

        if unit_name and hasattr(instance, "measure_unit"):
            unit, _ = MeasureUnit.objects.get_or_create(name=unit_name.strip())
            instance.measure_unit = unit

        if commit:
            instance.save()

        return instance


class MealAlternativeAdminForm(MeasureUnitManualForm):
    selected_item_label = forms.CharField(
        required=False,
        label="Seçilen Alternatif",
        widget=forms.TextInput(
            attrs={
                "class": "selected-item-label vTextField",
                "style": "min-width:260px; background:#0f172a; color:#f8fafc; border:1px solid #334155;",
            }
        ),
    )

    class Meta(MeasureUnitManualForm.Meta):
        model = MealAlternative
        fields = "__all__"
        exclude = ["measure_unit"]
        widgets = {
            "content_type": HiddenInput(attrs={"class": "alt-content-type-field"}),
            "object_id": HiddenInput(attrs={"class": "alt-object-id-field"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.item:
            self.fields["selected_item_label"].initial = getattr(self.instance.item, "name", "")

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        content_type = cleaned_data.get("content_type")

        if object_id and not content_type:
            raise forms.ValidationError(
                "Alternatif için öğe tipi otomatik doldurulamadı. Alternatifi yeniden seçin."
            )

        return cleaned_data


@admin.register(DietitianProfile)
class DietitianProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "title", "website"]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "height", "weight", "age", "gender", "activity_level"]
    search_fields = ["first_name", "last_name"]


@admin.register(DietRecommendation)
class DietRecommendationAdmin(admin.ModelAdmin):
    list_display = ["title"]
    search_fields = ["title"]


@admin.register(MeasureUnit)
class MeasureUnitAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(FoodGroup)
class FoodGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "carbohydrates", "protein", "fat"]
    search_fields = ["name"]


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ["name", "food_group", "measure_value", "measure_unit_text", "calories"]
    search_fields = ["name"]
    list_filter = ["food_group"]
    fields = ["food_group", "name", "measure_value", "measure_unit_text", "calories", "carbohydrates", "protein", "fat"]

    class Media:
        js = ("diet/js/food_group_autofill.js",)


class ExchangeItemInline(admin.TabularInline):
    model = ExchangeItem
    extra = 1
    autocomplete_fields = ["food", "recipe"]
    fields = ["food", "recipe", "reference_quantity", "unit"]


@admin.register(ExchangeGroup)
class ExchangeGroupAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    inlines = [ExchangeItemInline]


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    form = MeasureUnitManualForm
    extra = 0
    fields = ["name"] # Diğer alanlar kalabalık etmesin diye gizlendi (measure_value, measure_unit_text vb.)


class RecipePortionInline(admin.TabularInline):
    model = RecipePortion
    extra = 0
    fields = ["food_group", "amount"]

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "measure_value", "measure_unit_text", "calories"]
    search_fields = ["name"]
    inlines = [RecipeIngredientInline, RecipePortionInline]
    fields = [
        "name",
        "measure_value",
        "measure_unit_text",
        "instructions",
        "image",
        "youtube_link",
        "calories",
        "carbohydrates",
        "protein",
        "fat"
    ]

    class Media:
        js = ("diet/js/recipe_macro_calc.js",)


class MealAlternativeInline(nested_admin.NestedTabularInline):
    model = MealAlternative
    form = MealAlternativeAdminForm
    extra = 0
    fields = [
        "selected_item_label",
        "content_type",
        "object_id",
        "measure_value",
        "measure_unit_manual",
    ]
    verbose_name = "Alternatif"
    verbose_name_plural = "Alternatifler"


class MealFoodInline(nested_admin.NestedStackedInline):
    model = MealFood
    form = MeasureUnitManualForm
    extra = 0
    inlines = [MealAlternativeInline]
    autocomplete_fields = ["food"]
    fields = ["food", "measure_value", "measure_unit_manual"]


class MealRecipeInline(nested_admin.NestedStackedInline):
    model = MealRecipe
    form = MeasureUnitManualForm
    extra = 0
    inlines = [MealAlternativeInline]
    autocomplete_fields = ["recipe"]
    fields = ["recipe", "measure_value", "measure_unit_manual"]


class MealInline(nested_admin.NestedStackedInline):
    model = Meal
    extra = 0
    inlines = [MealFoodInline, MealRecipeInline]


class DietPlanTargetPortionInline(nested_admin.NestedTabularInline):
    model = DietPlanTargetPortion
    extra = 0
    fields = ["food_group", "target_amount"]
    classes = ["collapse"]

    def get_extra(self, request, obj=None, **kwargs):
        existing_count = obj.target_portions.count() if obj else 0
        total_groups = FoodGroup.objects.count()
        missing = total_groups - existing_count
        return missing if missing > 0 else 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        class CustomFormset(formset):
            def __init__(self, *args, **kwargs):
                if request.method == 'GET':
                    existing_groups = []
                    if obj:
                        existing_groups = list(obj.target_portions.values_list('food_group_id', flat=True))
                    
                    missing_groups = FoodGroup.objects.exclude(id__in=existing_groups)
                    
                    initial = kwargs.get('initial', [])
                    for fg in missing_groups:
                        initial.append({'food_group': fg.id, 'target_amount': 0})
                    
                    kwargs['initial'] = initial
                super().__init__(*args, **kwargs)
                
        return CustomFormset

@admin.register(DietPlan)
class DietPlanAdmin(nested_admin.NestedModelAdmin):
    list_display = ["id", "patient", "created_at", "pdf_indir_button"]
    search_fields = ["patient__first_name", "patient__last_name"]
    inlines = [DietPlanTargetPortionInline, MealInline]
    readonly_fields = ["pdf_indir_button"]
    autocomplete_fields = ["patient", "recommendations"]
    filter_horizontal = ["recommendations"]
    change_form_template = "admin/diet/dietplan/change_form.html"

    class Media:
        js = ("diet/js/live_dashboard.js",)

    def pdf_indir_button(self, obj):
        if obj.pk:
            return format_html(
                '<a class="button" href="/plan/{}/pdf/" target="_blank" '
                'style="background: #1A3C34; color: white; padding: 5px 10px; '
                'border-radius: 4px; text-decoration: none;">📄 PDF Çıktısı Al</a>',
                obj.pk
            )
        return "-"

    pdf_indir_button.short_description = "Aksiyon"