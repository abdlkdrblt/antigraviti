
content = r"""(function($) {
    let foodData = { foods: {}, recipes: {} };

    async function init() {
        console.log("Live Dashboard Init starting...");
        try {
            const response = await fetch('/api/food-data/');
            foodData = await response.json();
            console.log("Food data loaded:", Object.keys(foodData.foods).length, "foods");

            attachListeners();
            calculateTotals();
            patientChangeListener();
            console.log("Listeners attached successfully.");
        } catch (e) {
            console.error("Gıda verileri alınamadı:", e);
        }
    }

    function attachListeners() {
        // Herhangi bir input veya select değiştiğinde hesapla
        $(document).on('change', 'input, select, textarea', function() {
            calculateTotals();
        });

        // Autocomplete (Select2) seçimlerini anlık yakala
        $(document).on('select2:select', function() {
            calculateTotals();
        });

        // Nested Admin'de yeni satır eklendiğinde
        $(document).on('djn-formset:added', function() {
            calculateTotals();
        });

        // --- MASTER ROW & AUTO-SYNC ---
        $(document).on('input', 'input[name$="-measure_value"]', function() {
            const $qtyInput = $(this);
            const $row = $qtyInput.closest('.djn-inline-form');
            const mainQty = parseFloat($qtyInput.val()) || 0;

            const $container = $row.find('.smart-alternatives-box');
            if ($container.length > 0) {
                updateAlternativePorsiyon($container, mainQty);
            }
        });

        // Ana Besin/Tarif seçildiğinde Akıllı Rehberi aç
        $(document).on('change select2:select', 'select[name$="-food"], select[name$="-recipe"]', function() {
            const $select = $(this);
            const name = $select.attr('name');
            if (name && name.includes('-alternatives-')) return; 

            const type = (name && name.includes('-food')) ? 'food' : 'recipe';
            const objectId = $select.val();

            if (!objectId) return;
            showEquivalents($select, type, objectId);
        });
    }

    function patientChangeListener() {
        // Django Admin ID defaults: id_patient
        const $patientSelect = $('#id_patient');
        console.log("Attaching patientChangeListener to id_patient:", $patientSelect.length);
        
        // Listen both on standard change and select2:select
        $(document).on('change select2:select', '#id_patient', function() {
            const patientId = $(this).val();
            console.log("Patient changed to ID:", patientId);
            
            if (!patientId) {
                $('#bmr-val').text('0 kcal');
                $('#suggested-cal').text('0 kcal');
                return;
            }
            
            $.getJSON(`/api/patient-calories/${patientId}/`, function(data) {
                console.log("Patient data received:", data);
                if (data.status === 'success') {
                    $('#bmr-val').text(`${Math.round(data.bmr)} kcal`);
                    $('#suggested-cal').text(`${Math.round(data.maintenance_calories)} kcal`);
                    
                    // Autofill target calories if it's currently default (2000) or 0
                    const $targetCal = $('#id_target_calories');
                    if ($targetCal.val() == "2000" || !$targetCal.val() || $targetCal.val() == "0") {
                        $targetCal.val(Math.round(data.maintenance_calories)).trigger('change');
                    }
                }
            });
        });

        // Trigger on load if patient is already selected
        if ($patientSelect.val()) {
            console.log("Initial patient detected:", $patientSelect.val());
            $patientSelect.trigger('change');
        }
    }

    async function showEquivalents($selectElem, type, objectId) {
        $.getJSON('/api/exchanges/', {id: objectId, type: type}, function(data) {
            const $row = $selectElem.closest('.djn-item');
            const $qtyInput = $row.find('input[name$="-measure_value"]');
            let $container = $row.find('.smart-alternatives-box');

            if ($container.length === 0) {
                $container = $('<div class="smart-alternatives-box" style="margin-top: 10px; padding: 12px; background: #f0fdf4; border: 1px dashed #10b981; border-radius: 8px;"></div>');
                // field-food or field-recipe
                $selectElem.parent().append($container);
            }

            $container.empty();
            if (!data.exchanges || data.exchanges.length === 0) {
                $container.html('<i style="color:#6b7280; font-size:13px;">Klinik bir Değişim Grubu bulunamadı.</i>');
                return;
            }

            let html = `<b style="color:#059669; font-size:13px; margin-bottom: 8px; display:block;">✨ Akıllı Rehber: ${data.group_name}</b>`;
            const mainQty = parseFloat($qtyInput.val()) || 1;

            data.exchanges.forEach(ex => {
                let icon = ex.type === 'food' ? '🍏' : '🥗';
                let altQty = (mainQty * ex.ratio).toFixed(1);
                
                html += `   
                    <span class="alt-item"
                          data-id="${ex.id}"
                          data-ct="${ex.content_type_id}"
                          data-ratio="${ex.ratio}"
                          data-unit="${ex.unit}"
                          data-name="${ex.name}"
                          style="display:inline-block; margin: 4px; padding: 6px 12px; background: white; border: 1px solid #10b981; border-radius: 20px; font-size: 13px; color:#065f46; cursor:pointer; transition: all 0.2s;"
                          onmouseover="this.style.background='#dcfce7'"
                          onmouseout="this.style.background='white'">
                        ${icon} <b>${ex.name}</b>: <span class="alt-qty">${parseFloat(altQty)}</span> ${ex.unit}
                    </span>`;
            });
            $container.html(html);
        });
    }

    $(document).on('click', '.alt-item', function() {
        const $item = $(this);
        const $row = $item.closest('.djn-item'); 
        const $alternativesGroup = $row.find('.djn-group[data-inline-model="diet_mealalternative"]');
        const $addButton = $alternativesGroup.find('.djn-add-handler').last();

        if ($addButton.length > 0) {
            $addButton.trigger('click');
            setTimeout(() => {
                const $newRow = $alternativesGroup.find('.djn-inline-form:not(.djn-empty-form)').last();
                $newRow.find('select[name$="-content_type"]').val($item.data('ct')).trigger('change');
                $newRow.find('input[name$="-object_id"]').val($item.data('id')).trigger('change');

                const mainQty = parseFloat($row.find('input[name$="-measure_value"]').val()) || 1;
                const ratio = parseFloat($item.data('ratio'));
                $newRow.find('input[name$="-measure_value"]').val((mainQty * ratio).toFixed(2)).trigger('change');
                $newRow.find('input[name$="-measure_unit_manual"]').val($item.data('unit')).trigger('change');

                $item.css('background', '#10b981').css('color', 'white');
                setTimeout(() => $item.css('background', 'white').css('color', '#065f46'), 500);
            }, 100);
        }
    });

    function updateAlternativePorsiyon($container, mainQty) {
        $container.find('.alt-item').each(function() {
            const ratio = parseFloat($(this).data('ratio'));
            const newQty = (mainQty * ratio).toFixed(1);
            $(this).find('.alt-qty').text(parseFloat(newQty));
        });
    }

    function calculateTotals() {
        let totalCal = 0, totalCho = 0, totalProt = 0, totalFat = 0;

        const targetCal = parseFloat($('#id_target_calories').val() || 0);
        const targetCarbPct = parseInt($('#id_target_carb_percent').val() || 50);
        const targetProtPct = parseInt($('#id_target_prot_percent').val() || 20);
        const targetFatPct = parseInt($('#id_target_fat_percent').val() || 30);

        const tChoGrams = (targetCal * (targetCarbPct/100)) / 4;
        const tProtGrams = (targetCal * (targetProtPct/100)) / 4;
        const tFatGrams = (targetCal * (targetFatPct/100)) / 9;

        $('select[name$="-food"]').each(function() {
            if ($(this).closest('.empty-form, .djn-empty-form, [name*="-alternatives-"]').length > 0) return;
            calculateItem($(this), 'foods');
        });

        $('select[name$="-recipe"]').each(function() {
            if ($(this).closest('.empty-form, .djn-empty-form, [name*="-alternatives-"]').length > 0) return;
            calculateItem($(this), 'recipes');
        });

        function calculateItem($select, dataKey) {
            const id = $select.val();
            const row = $select.closest('.djn-inline-form');
            const measureValue = parseFloat(row.find('input[name$="-measure_value"]').val() || 1);

            if (id && foodData[dataKey][id]) {
                const item = foodData[dataKey][id];
                totalCal += item.cal * measureValue;
                totalCho += item.cho * measureValue;
                totalProt += item.prot * measureValue;
                totalFat += item.fat * measureValue;
            }
        }

        updateDashboard('total-cal', 'cal-progress', totalCal, targetCal, 'kcal');
        updateDashboard('total-cho', 'cho-progress', totalCho, tChoGrams, 'g');
        updateDashboard('total-prot', 'prot-progress', totalProt, tProtGrams, 'g');
        updateDashboard('total-fat', 'fat-progress', totalFat, tFatGrams, 'g');
    }

    function updateDashboard(id, progressId, current, target, unit) {
        $(`#${id}`).text(`${Math.round(current)} / ${Math.round(target)} ${unit}`);
        let percent = target > 0 ? (current / target) * 100 : 0;
        $(`#${progressId}`).css('width', Math.min(percent, 100) + '%').removeClass('ideal over-limit under');

        if (target === 0) return;
        const ratio = current / target;
        if (ratio > 1.1) $(`#${progressId}`).addClass('over-limit');
        else if (ratio >= 0.9) $(`#${progressId}`).addClass('ideal');
        else $(`#${progressId}`).addClass('under');
    }

    $(document).ready(init);

})(django.jQuery);
"""

import os
path = r"c:\Users\Aslınur Bulut\.gemini\antigravity\scratch\dietitian_app\diet\static\diet\js\live_dashboard.js"
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("File fixed successfully.")
