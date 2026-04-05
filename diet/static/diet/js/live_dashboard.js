(function ($) {
    let foodData = { foods: {}, recipes: {}, content_types: {}, food_groups: {} };

    async function init() {
        console.log("Live Dashboard init starting...");
        try {
            const response = await fetch("/api/food-data/");
            foodData = await response.json();
            console.log("Food data loaded successfully.");

            attachListeners();
            calculateTotals();
            patientChangeListener();
            initEquivalents();
            updateAlternativeLabels();
            console.log("All systems initialized.");
        } catch (e) {
            console.error("Gıda verileri alınamadı:", e);
        }
    }

    function getAlternativeGroup($row) {
        return $row.find('.djn-group[data-inline-model*="mealalternative"]');
    }

    function getContentTypeField($row) {
        return $row.find('input[name$="-content_type"], select[name$="-content_type"]').first();
    }

    function getObjectIdField($row) {
        return $row.find('input[name$="-object_id"]').first();
    }

    function getItemNameByContentTypeAndId(contentTypeId, objectId) {
        if (!contentTypeId || !objectId) return "";

        const ct = String(contentTypeId);
        const oid = String(objectId);

        if (
            String(foodData.content_types?.food || "") === ct &&
            foodData.foods[oid]
        ) {
            return foodData.foods[oid].name;
        }

        if (
            String(foodData.content_types?.recipe || "") === ct &&
            foodData.recipes[oid]
        ) {
            return foodData.recipes[oid].name;
        }

        if (foodData.foods[oid]) return foodData.foods[oid].name;
        if (foodData.recipes[oid]) return foodData.recipes[oid].name;

        return "";
    }

    function attachListeners() {
        $(document).on("change", "input, select, textarea", function () {
            calculateTotals();
        });

        $(document).on("select2:select", function () {
            calculateTotals();
        });

        $(document).on("djn-formset:added", function (event, $row) {
            calculateTotals();
            updateAlternativeLabels();

            if ($row && $row.length) {
                const $parentItem = $row.closest(".djn-item");
                const $guide = $parentItem.find(".smart-alternatives-box");
                const mainQty = parseFloat(
                    $parentItem.find('input[name$="-measure_value"]').first().val() || 1
                );
                if ($guide.length) {
                    updateAlternativePorsiyon($guide, mainQty);
                }
            }
        });

        $(document).on("input", 'input[name$="-measure_value"]', function () {
            const $qtyInput = $(this);
            const name = $qtyInput.attr("name") || "";

            if (name.includes("-alternatives-")) {
                // Alternatif miktar değiştiğinde dashboard'u güncelle (tercihe bağlı)
                return;
            }

            const $row = $qtyInput.closest(".djn-inline-form");
            const mainQty = parseFloat($qtyInput.val()) || 0;
            const $container = $row.find(".smart-alternatives-box");

            if ($container.length > 0) {
                updateAlternativePorsiyon($container, mainQty);
                syncExistingAlternatives($row, mainQty); // Mevcut alternatifleri de anlık güncelle
            }
        });

        $(document).on(
            "change select2:select",
            'select[name$="-food"], select[name$="-recipe"]',
            function () {
                const $select = $(this);
                const name = $select.attr("name") || "";

                if (name.includes("-alternatives-")) return;

                const type = name.includes("-food") ? "food" : "recipe";
                const objectId = $select.val();

                if (!objectId) return;
                showEquivalents($select, type, objectId);
            }
        );
    }

    function syncExistingAlternatives($mainRow, mainQty) {
        const $altGroup = getAlternativeGroup($mainRow);
        $altGroup.find(".djn-inline-form:not(.djn-empty-form)").each(function() {
            const $altRow = $(this);
            const ratio = parseFloat($altRow.data("ratio")) || 1;
            const oid = getObjectIdField($altRow).val();
            const ct = getContentTypeField($altRow).val();
            const name = getItemName(ct, oid);
            
            const $qtyField = $altRow.find('input[name$="-measure_value"]');
            if ($qtyField.length) {
                $qtyField.val((mainQty * ratio).toFixed(2)).trigger("change");
            }
            
            if (name) {
                setLabelValue($altRow, name);
            }
        });
    }

    function initEquivalents() {
        $('select[name$="-food"], select[name$="-recipe"]').each(function () {
            const $select = $(this);
            const val = $select.val();
            const name = $select.attr("name") || "";

            if (val && name && !name.includes("-alternatives-") && !name.includes("__prefix__")) {
                const type = name.includes("-food") ? "food" : "recipe";
                showEquivalents($select, type, val);
            }
        });
    }

    function patientChangeListener() {
        const $patientSelect = $("#id_patient");

        $(document).on("change select2:select", "#id_patient", function () {
            const patientId = $(this).val();

            if (!patientId) {
                $("#bmr-val").text("0 kcal");
                $("#suggested-cal").text("0 kcal");
                return;
            }

            $.getJSON(`/api/patient-calories/${patientId}/`, function (data) {
                if (data.status === "success") {
                    $("#bmr-val").text(`${Math.round(data.bmr)} kcal`);
                    $("#suggested-cal").text(`${Math.round(data.maintenance_calories)} kcal`);

                    const $targetCal = $("#id_target_calories");
                    if (
                        $targetCal.val() === "2000" ||
                        !$targetCal.val() ||
                        $targetCal.val() === "0"
                    ) {
                        $targetCal.val(Math.round(data.maintenance_calories)).trigger("change");
                    }
                }
            });
        });

        if ($patientSelect.val()) $patientSelect.trigger("change");
    }

    function showEquivalents($selectElem, type, objectId) {
        $.getJSON("/api/exchanges/", { id: objectId, type: type }, function (data) {
            const $row = $selectElem.closest(".djn-item");
            const $qtyInput = $row.find('input[name$="-measure_value"]').first();
            let $container = $row.find(".smart-alternatives-box");

            if ($container.length === 0) {
                $container = $(
                    '<div class="smart-alternatives-box" style="margin-top: 10px; padding: 12px; background: #f0fdf4; border: 1px dashed #10b981; border-radius: 8px;"></div>'
                );
                $selectElem.parent().append($container);
            }

            $container.empty();

            if (!data.exchanges || data.exchanges.length === 0) {
                $container.html(
                    '<i style="color:#6b7280; font-size:13px;">Klinik bir Değişim Grubu bulunamadı.</i>'
                );
                return;
            }

            let html = `<b style="color:#059669; font-size:13px; margin-bottom: 8px; display:block;">✨ Akıllı Rehber: ${data.group_name}</b>`;
            const mainQty = parseFloat($qtyInput.val()) || 1;

            const selectedKeys = [];
            const $altGroup = getAlternativeGroup($row);

            $altGroup.find(".djn-inline-form:not(.djn-empty-form)").each(function () {
                const $altRow = $(this);
                const oid = getObjectIdField($altRow).val();
                const ct = getContentTypeField($altRow).val();

                if (oid && ct) {
                    selectedKeys.push(`${ct}:${oid}`);
                }
            });

            data.exchanges.forEach((ex) => {
                const icon = ex.type === "food" ? "🍏" : "🥗";
                const altQty = (mainQty * ex.ratio).toFixed(1);
                const key = `${ex.content_type_id}:${ex.id}`;
                const isSelected = selectedKeys.includes(key);

                html += `
                    <span class="alt-item ${isSelected ? "is-selected" : ""}"
                          data-id="${ex.id}"
                          data-ct="${ex.content_type_id}"
                          data-ratio="${ex.ratio}"
                          data-unit="${ex.unit}"
                          data-name="${ex.name}">
                        ${icon} <b>${ex.name}</b>: <span class="alt-qty">${parseFloat(altQty)}</span> ${ex.unit}
                    </span>`;
            });

            $container.html(html);
        });
    }

    function getItemName(ct, oid) {
        if (!oid || !ct) return "";
        const s_oid = String(oid);
        const s_ct = String(ct);
        const ct_food = String(foodData.content_types?.food);
        const ct_recipe = String(foodData.content_types?.recipe);

        if (s_ct === ct_food && foodData.foods[s_oid]) return foodData.foods[s_oid].name;
        if (s_ct === ct_recipe && foodData.recipes[s_oid]) return foodData.recipes[s_oid].name;

        // Fallback: search both
        if (foodData.foods[s_oid]) return foodData.foods[s_oid].name;
        if (foodData.recipes[s_oid]) return foodData.recipes[s_oid].name;
        return "";
    }

    function setLabelValue($row, itemName) {
        if (!itemName) return;
        const mainInput = $row.closest(".djn-item").find('input[name$="-measure_value"]').first();
        const mainQty = parseFloat(mainInput.val()) || 1;
        const ratio = parseFloat($row.data("ratio")) || 1;
        
        // Etiket formatı: "+ Alternatif: 3 18 adet orta boy Çilek"
        const displayQty = parseFloat((mainQty * ratio).toFixed(2));
        const unitLabel = $row.find('input[name$="-measure_unit_manual"]').val() || "Birim";
        const fullLabel = `+ Alternatif: ${displayQty} ${unitLabel} ${itemName}`;

        const fillAction = () => {
            const $label = $row.find('input[name$="-selected_item_label"], .selected-item-label').first();
            if ($label.length) {
                $label.val(fullLabel).attr('value', fullLabel);
                $label.trigger("change").trigger("input");
            }
        };
        
        [0, 50, 150, 400, 800, 1500].forEach(delay => {
            setTimeout(fillAction, delay);
        });
    }

    function setAlternativeValues($row, id, ct, name, unit, mainQty, ratio) {
        $row.attr("data-ratio", ratio).data("ratio", ratio); // Sync için orantıyı kaydet
        
        const fill = () => {
            const ctField = $row.find(".alt-content-type-field, [name$='-content_type']").first();
            const oidField = $row.find(".alt-object-id-field, [name$='-object_id']").first();
            const qtyField = $row.find('input[name$="-measure_value"]');
            const unitField = $row.find('input[name$="-measure_unit_manual"]');

            if (ctField.length && oidField.length) {
                ctField.val(ct).trigger("change");
                oidField.val(id).trigger("change");
                qtyField.val((mainQty * ratio).toFixed(2)).trigger("change");
                unitField.val(unit).trigger("change");
                setLabelValue($row, name);
            }
        };

        // Django Nessted Admin'in değerleri sıfırlamasını engellemek için periyodik zorla
        [0, 30, 100, 300, 600, 1200].forEach(delay => {
            setTimeout(fill, delay);
        });
    }

    $(document).on("click", ".alt-item", function () {
        const $item = $(this);
        const $row = $item.closest(".djn-inline-form");
        const $altGroup = $row.find('.djn-group[data-inline-model*="mealalternative"]');

        const id = String($item.data("id"));
        const ct = String($item.data("ct"));
        const name = String($item.data("name") || "");
        const unit = String($item.data("unit") || "Birim");
        const ratio = parseFloat($item.data("ratio")) || 1;
        const mainQty = parseFloat($row.find('input[name$="-measure_value"]').val()) || 1;

        let exists = false;
        $altGroup.find(".djn-inline-form").not(".djn-empty-form").each(function () {
            const $r = $(this);
            const r_oid = $r.find(".alt-object-id-field, [name$='-object_id']").val();
            const r_ct = $r.find(".alt-content-type-field, [name$='-content_type']").val();
            if (String(r_oid) === id && String(r_ct) === ct) {
                $r.find(".djn-remove-handler").click();
                exists = true;
                return false;
            }
        });

        if (exists) {
            $item.removeClass("is-selected");
            return;
        }

        const $addButton = $altGroup.find(".djn-add-handler").last();
        $addButton.trigger("click");

        let tryCount = 0;
        const waitForRow = () => {
            tryCount++;
            let $newRow = null;
            $altGroup.find(".djn-inline-form").not(".djn-empty-form").each(function () {
                const $r = $(this);
                const r_oid = $r.find(".alt-object-id-field, [name$='-object_id']").val();
                if (!r_oid) $newRow = $r;
            });
            if (!$newRow) $newRow = $altGroup.find(".djn-inline-form").not(".djn-empty-form").last();

            if ($newRow && $newRow.length && !$newRow.find(".alt-object-id-field, [name$='-object_id']").val()) {
                setAlternativeValues($newRow, id, ct, name, unit, mainQty, ratio);
                $item.addClass("is-selected");
                return;
            }
            if (tryCount < 15) setTimeout(waitForRow, 50);
        };
        setTimeout(waitForRow, 30);
    });

    function updateAlternativeLabels() {
        $('.djn-group[data-inline-model*="mealalternative"] .djn-inline-form:not(.djn-empty-form)').each(function () {
            const $row = $(this);
            const oid = $row.find(".alt-object-id-field, [name$='-object_id']").val();
            const ct = $row.find(".alt-content-type-field, [name$='-content_type']").val();
            if (!oid || !ct) return;

            const name = getItemName(ct, oid);
            if (name) {
                setLabelValue($row, name);
            }
        });
    }

    function updateAlternativePorsiyon($container, mainQty) {
        $container.find(".alt-item").each(function () {
            const ratio = parseFloat($(this).data("ratio")) || 1;
            const newQty = (mainQty * ratio).toFixed(1);
            $(this).find(".alt-qty").text(parseFloat(newQty));
        });
    }

    let isUpdatingFromPortions = false;

    function calculateTotals() {
        if (isUpdatingFromPortions) return;

        let totalCho = 0;
        let totalProt = 0;
        let totalFat = 0;

        let actualPortions = {}; 
        let targetPortions = {}; 

        let sumPortionCho = 0;
        let sumPortionProt = 0;
        let sumPortionFat = 0;

        $('.djn-group[data-inline-model*="dietplantargetportion"] .djn-inline-form:not(.djn-empty-form)').each(function() {
            const groupId = $(this).find('select[name$="-food_group"]').val();
            const targetVal = parseFloat($(this).find('input[name$="-target_amount"]').val() || 0);
            if (groupId) {
                targetPortions[groupId] = (targetPortions[groupId] || 0) + targetVal;
                
                const group = foodData.food_groups[groupId];
                if (group) {
                    sumPortionCho += (group.cho * targetVal);
                    sumPortionProt += (group.prot * targetVal);
                    sumPortionFat += (group.fat * targetVal);
                }
            }
        });

        if (Object.keys(targetPortions).length > 0) {
            const portionTotalCal = (sumPortionCho * 4) + (sumPortionProt * 4) + (sumPortionFat * 9);
            
            if (portionTotalCal > 0) {
                const pctCho = Math.round((sumPortionCho * 4 / portionTotalCal) * 100);
                const pctProt = Math.round((sumPortionProt * 4 / portionTotalCal) * 100);
                const pctFat = Math.round((sumPortionFat * 9 / portionTotalCal) * 100);

                const $targetCal = $("#id_target_calories");
                const $targetChoPct = $("#id_target_carb_percent");
                const $targetProtPct = $("#id_target_prot_percent");
                const $targetFatPct = $("#id_target_fat_percent");

                isUpdatingFromPortions = true;
                if (Math.round(parseFloat($targetCal.val())) !== Math.round(portionTotalCal)) {
                    $targetCal.val(Math.round(portionTotalCal)).trigger("change");
                }
                if (parseInt($targetChoPct.val()) !== pctCho) {
                    $targetChoPct.val(pctCho).trigger("change");
                }
                if (parseInt($targetProtPct.val()) !== pctProt) {
                    $targetProtPct.val(pctProt).trigger("change");
                }
                if (parseInt($targetFatPct.val()) !== pctFat) {
                    $targetFatPct.val(pctFat).trigger("change");
                }
                isUpdatingFromPortions = false;
            }
        }

        const targetCal = parseFloat($("#id_target_calories").val() || 0);
        const targetCarbPct = parseInt($("#id_target_carb_percent").val() || 50, 10);
        const targetProtPct = parseInt($("#id_target_prot_percent").val() || 20, 10);
        const targetFatPct = parseInt($("#id_target_fat_percent").val() || 30, 10);

        const tChoGrams = (targetCal * (targetCarbPct / 100)) / 4;
        const tProtGrams = (targetCal * (targetProtPct / 100)) / 4;
        const tFatGrams = (targetCal * (targetFatPct / 100)) / 9;

        $('select[name$="-food"]').each(function () {
            if ($(this).closest(".empty-form, .djn-empty-form, [name*='-alternatives-']").length > 0) return;
            
            const id = String($(this).val() || "");
            const row = $(this).closest(".djn-inline-form");
            const measureValue = parseFloat(row.find('input[name$="-measure_value"]').val() || 1);

            if (id && foodData.foods[id]) {
                const item = foodData.foods[id];
                totalCho += item.cho * measureValue;
                totalProt += item.prot * measureValue;
                totalFat += item.fat * measureValue;

                if (item.group_id) {
                    const gid = String(item.group_id);
                    actualPortions[gid] = (actualPortions[gid] || 0) + measureValue;
                }
            }
        });

        $('select[name$="-recipe"]').each(function () {
            if ($(this).closest(".empty-form, .djn-empty-form, [name*='-alternatives-']").length > 0) return;
            
            const id = String($(this).val() || "");
            const row = $(this).closest(".djn-inline-form");
            const measureValue = parseFloat(row.find('input[name$="-measure_value"]').val() || 1);

            if (id && foodData.recipes[id]) {
                const item = foodData.recipes[id];
                totalCho += item.cho * measureValue;
                totalProt += item.prot * measureValue;
                totalFat += item.fat * measureValue;

                if (item.portions) {
                    for (const [gid, amount] of Object.entries(item.portions)) {
                        actualPortions[gid] = (actualPortions[gid] || 0) + (amount * measureValue);
                    }
                }
            }
        });

        const currentTotalCal = (totalCho * 4) + (totalProt * 4) + (totalFat * 9);

        updateDashboard("total-cal", "cal-progress", currentTotalCal, targetCal, "kcal");
        updateDashboard("total-cho", "cho-progress", totalCho, tChoGrams, "g");
        updateDashboard("total-prot", "prot-progress", totalProt, tProtGrams, "g");
        updateDashboard("total-fat", "fat-progress", totalFat, tFatGrams, "g");

        updateExchangeTracker(actualPortions, targetPortions);
    }

    function updateExchangeTracker(actual, target) {
        const $container = $("#exchange-analysis-panel");
        $container.empty();

        const allGroupIds = new Set([...Object.keys(actual), ...Object.keys(target)]);
        
        let portionTotalCal = 0;

        if (allGroupIds.size === 0) {
            $container.hide();
            return;
        }
        $container.show();

        allGroupIds.forEach(gid => {
            const group = foodData.food_groups[gid];
            const groupName = group?.name || "Grup " + gid;
            const aVal = actual[gid] || 0;
            const tVal = target[gid] || 0;
            
            if (tVal === 0 && aVal === 0) return;

            if (group) {
                portionTotalCal += tVal * (group.cho * 4 + group.prot * 4 + group.fat * 9);
            }

            let statusClass = "";
            if (tVal > 0) {
                if (aVal > tVal + 0.1) statusClass = "over";
                else if (aVal >= tVal - 0.1) statusClass = "completed";
            }

            const html = `
                <div class="exchange-box ${statusClass}">
                    <div class="exchange-label">${groupName}</div>
                    <div class="exchange-value">${parseFloat(aVal.toFixed(1))} <span>/ ${parseFloat(tVal.toFixed(1))}</span></div>
                </div>
            `;
            $container.append(html);
        });

        const summaryHtml = `
            <div class="exchange-box" style="background: rgba(16, 185, 129, 0.2); border: 2px solid #10b981; min-width: 140px;">
                <div class="exchange-label" style="color: #fff">Hedef Kalori (Porsiyon)</div>
                <div class="exchange-value" style="color: #10b981">${Math.round(portionTotalCal)} kcal</div>
            </div>
        `;
        $container.append(summaryHtml);
    }

    function updateDashboard(id, progressId, current, target, unit) {
        $(`#${id}`).text(`${Math.round(current)} / ${Math.round(target)} ${unit}`);

        const percent = target > 0 ? (current / target) * 100 : 0;
        $(`#${progressId}`)
            .css("width", `${Math.min(percent, 100)}%`)
            .removeClass("ideal over-limit under");

        if (target === 0) return;

        const ratio = current / target;
        if (ratio > 1.1) {
            $(`#${progressId}`).addClass("over-limit");
        } else if (ratio >= 0.9) {
            $(`#${progressId}`).addClass("ideal");
        } else {
            $(`#${progressId}`).addClass("under");
        }
    }

    $(document).ready(init);
})(django.jQuery);