from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify

from .models import DietPlan, Patient, Food, Recipe, FoodGroup, ExchangeItem
from .pdf_generator import DietPDFGenerator


def diet_plan_detail_view(request, pk):
    """Mevcut HTML bazlı detay sayfası."""
    diet_plan = get_object_or_404(
        DietPlan.objects.prefetch_related(
            "meals__mealfood_set__alternatives",
            "meals__mealrecipe_set__recipe",
            "meals__mealrecipe_set__alternatives",
        ),
        pk=pk
    )

    return render(request, "diet/diet_plan_detail.html", {
        "diet_plan": diet_plan
    })


def export_pdf_view(request, pk):
    """ReportLab Platypus kullanarak HTML'siz PDF üretir."""
    diet_plan = get_object_or_404(
        DietPlan.objects.prefetch_related(
            "meals__mealfood_set__alternatives",
            "meals__mealrecipe_set__recipe",
            "meals__mealrecipe_set__alternatives",
        ),
        pk=pk
    )

    generator = DietPDFGenerator(diet_plan)
    pdf_content = generator.generate()

    filename = slugify(f"diyet-plani-{diet_plan.patient}") or "diyet-plani"

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}.pdf"'
    response.write(pdf_content)
    return response


def get_patient_calories(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return JsonResponse({
        "status": "success",
        "maintenance_calories": patient.calculate_maintenance_calories(),
        "bmr": patient.calculate_bmr()
    })


def get_exchanges(request):
    """Belirli bir Besin veya Tarif ID'si için o gruptaki eşdeğer değişimleri döner."""
    obj_id = request.GET.get("id")
    obj_type = request.GET.get("type")  # food / recipe

    if not obj_id or not obj_type:
        return JsonResponse({"error": "Missing parameters"}, status=400)

    try:
        if obj_type == "food":
            picked_item = ExchangeItem.objects.select_related("group").filter(food_id=obj_id).first()
        elif obj_type == "recipe":
            picked_item = ExchangeItem.objects.select_related("group").filter(recipe_id=obj_id).first()
        else:
            return JsonResponse({"error": "Invalid type"}, status=400)

        if not picked_item:
            return JsonResponse({
                "status": "empty",
                "exchanges": [],
                "info": "Bu ürün herhangi bir Değişim Grubuna dahil değil."
            })

        group = picked_item.group
        exchanges = []

        for item in group.items.select_related("food", "recipe", "unit").all():
            target_obj = item.food if item.food else item.recipe
            if not target_obj:
                continue

            target_type = "food" if item.food else "recipe"
            target_content_type_id = ContentType.objects.get_for_model(target_obj).id

            if float(picked_item.reference_quantity) == 0:
                ratio = 1.0
            else:
                ratio = float(item.reference_quantity / picked_item.reference_quantity)

            exchanges.append({
                "id": target_obj.id,
                "type": target_type,
                "content_type_id": target_content_type_id,
                "name": target_obj.name,
                "unit": item.unit.name if item.unit else "Birim",
                "ratio": ratio,
                "ref_qty": float(item.reference_quantity),
            })

        return JsonResponse({
            "status": "success",
            "group_name": group.name,
            "source_ref": float(picked_item.reference_quantity),
            "exchanges": exchanges,
        })

    except (ExchangeItem.DoesNotExist, ExchangeItem.MultipleObjectsReturned):
        return JsonResponse({
            "status": "empty",
            "exchanges": [],
            "info": "Bu ürün herhangi bir Değişim Grubuna dahil değil."
        })


def get_food_data(request):
    """Admin panelindeki JS'in hızlı hesaplama yapabilmesi için tüm besin/tarif verilerini döner."""
    food_content_type_id = ContentType.objects.get_for_model(Food).id
    recipe_content_type_id = ContentType.objects.get_for_model(Recipe).id

    foods = {}
    for f in Food.objects.all():
        foods[str(f.id)] = {
            "id": f.id,
            "type": "food",
            "content_type_id": food_content_type_id,
            "cal": float(f.calories),
            "cho": float(f.carbohydrates),
            "prot": float(f.protein),
            "fat": float(f.fat),
            "name": f.name,
            "group_id": f.food_group_id if hasattr(f, "food_group_id") else None,
        }

    recipes = {}
    for r in Recipe.objects.select_related("food_group").prefetch_related("portions").all():
        portions = {str(p.food_group_id): float(p.amount) for p in r.portions.all()}
        recipes[str(r.id)] = {
            "id": r.id,
            "type": "recipe",
            "content_type_id": recipe_content_type_id,
            "cal": float(r.calories or 0),
            "cho": float(r.carbohydrates or 0),
            "prot": float(r.protein or 0),
            "fat": float(r.fat or 0),
            "name": r.name,
            "group_id": r.food_group_id if hasattr(r, "food_group_id") else None,
            "portions": portions,
        }

    return JsonResponse({
        "foods": foods,
        "recipes": recipes,
        "content_types": {
            "food": food_content_type_id,
            "recipe": recipe_content_type_id,
        },
        "food_groups": {
            g.id: {
                "name": g.name,
                "cho": float(g.carbohydrates or 0),
                "prot": float(g.protein or 0),
                "fat": float(g.fat or 0)
            } for g in FoodGroup.objects.all()
        }
    })


def get_food_group_data(request):
    """Admin panelinde besin grubu seçildiğinde makroları otomatik doldurmak için."""
    groups = {
        g.id: {
            "cho": float(g.carbohydrates),
            "prot": float(g.protein),
            "fat": float(g.fat)
        }
        for g in FoodGroup.objects.all()
    }
    return JsonResponse({"groups": groups})


def get_exchange_list(request, content_type_id, object_id):
    """
    Belirli bir besin/tarif için ExchangeGroup üyelerini döner.
    """
    ct = get_object_or_404(ContentType, id=content_type_id)

    try:
        if ct.model == "food":
            source_item = ExchangeItem.objects.get(food_id=object_id)
        else:
            source_item = ExchangeItem.objects.get(recipe_id=object_id)

        group = source_item.group
        exchanges = []

        for item in group.items.all():
            target_obj = item.food if item.food else item.recipe
            if not target_obj:
                continue

            ratio = float(item.reference_quantity / source_item.reference_quantity)

            exchanges.append({
                "id": target_obj.id,
                "content_type_id": ContentType.objects.get_for_model(target_obj).id,
                "name": target_obj.name,
                "unit": item.unit.name if item.unit else "Birim",
                "ratio": ratio,
                "ref_qty": float(item.reference_quantity)
            })

        return JsonResponse({
            "status": "success",
            "group_name": group.name,
            "source_item_name": (source_item.food or source_item.recipe).name,
            "exchanges": exchanges
        })

    except (ExchangeItem.DoesNotExist, ExchangeItem.MultipleObjectsReturned):
        return JsonResponse({
            "status": "empty",
            "exchanges": [],
            "message": "Bu öğe bir değişim grubunda değil."
        })