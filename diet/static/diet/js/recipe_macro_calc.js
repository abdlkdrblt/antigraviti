document.addEventListener("DOMContentLoaded", function () {
    const carbInput = document.getElementById("id_carbohydrates");
    const protInput = document.getElementById("id_protein");
    const fatInput = document.getElementById("id_fat");
    const calInput = document.getElementById("id_calories");

    // Eğer Recipe admin formunda değilsek çık
    if (!carbInput || !protInput || !fatInput || !calInput) return;

    let foodGroupsData = {};

    // API'den Besin Grupları verisini çek
    fetch("/api/food-groups/")
        .then(response => response.json())
        .then(data => {
            foodGroupsData = data.groups;
            // İlk yüklemede de hesapla? 
            // Belki kullanıcı mevcut veriyi bozmak istemez, 
            // o yüzden sadece bir değişiklik olduğunda tetiklemek daha güvenli.
        })
        .catch(err => console.error("Besin grupları yüklenirken hata:", err));

    function calculateTotals() {
        if (!foodGroupsData || Object.keys(foodGroupsData).length === 0) return;

        let totalCho = 0;
        let totalProt = 0;
        let totalFat = 0;

        // RecipePortionInline prefix'i "portions"
        const rows = document.querySelectorAll('.dynamic-portions, [id^="portions-"].inline-related:not(.empty-form)');
        
        rows.forEach(row => {
            // Silinmiş satırları atla
            const deleteInput = row.querySelector('input[id$="-DELETE"]');
            if (deleteInput && deleteInput.checked) return;

            const groupSelect = row.querySelector('select[id$="-food_group"]');
            const amountInput = row.querySelector('input[id$="-amount"]');

            if (groupSelect && amountInput) {
                const groupId = groupSelect.value;
                const amount = parseFloat(amountInput.value) || 0;

                if (groupId && foodGroupsData[groupId]) {
                    const group = foodGroupsData[groupId];
                    totalCho += group.cho * amount;
                    totalProt += group.prot * amount;
                    totalFat += group.fat * amount;
                }
            }
        });

        const totalCal = (totalCho * 4) + (totalProt * 4) + (totalFat * 9);

        // Değerler değişmiş mi kontrol et (sonsuz döngüyü veya gereksiz titremeyi önlemek için)
        if (
            carbInput.value != totalCho.toFixed(2) ||
            protInput.value != totalProt.toFixed(2) ||
            fatInput.value != totalFat.toFixed(2) ||
            calInput.value != totalCal.toFixed(2)
        ) {
            carbInput.value = totalCho.toFixed(2);
            protInput.value = totalProt.toFixed(2);
            fatInput.value = totalFat.toFixed(2);
            calInput.value = totalCal.toFixed(2);
            
            // Görsel geri bildirim
            [carbInput, protInput, fatInput, calInput].forEach(el => {
                el.style.transition = "background-color 0.3s";
                el.style.backgroundColor = "#e8f5e9"; 
                setTimeout(() => { el.style.backgroundColor = ""; }, 600);
            });
        }
    }

    // Event Delegation: Inline içindeki herhangi bir değişiklik için
    const portionsInline = document.getElementById("portions-group");
    if (portionsInline) {
        portionsInline.addEventListener("change", function (e) {
            if (e.target.id.includes("-food_group") || e.target.id.includes("-amount") || e.target.id.includes("-DELETE")) {
                calculateTotals();
            }
        });
        
        portionsInline.addEventListener("input", function (e) {
            if (e.target.id.includes("-amount")) {
                calculateTotals();
            }
        });
    }
    
    // Ayrıca yeni satırlar eklendiğinde (django admin add-row butonu)
    // Django admin "formset:added" event'ini ateşler.
    $(document).on('formset:added', function(event, $row, formsetName) {
        if (formsetName === 'portions') {
            // Yeni satırdaki alanlara da listener eklemek gerekirse 
            // (gerçi event delegation kullandık ama miktar için input event'i önemli)
        }
    });
});
