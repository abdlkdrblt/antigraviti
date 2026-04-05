document.addEventListener("DOMContentLoaded", function () {
    const foodGroupSelect = document.getElementById("id_food_group");
    const carbInput = document.getElementById("id_carbohydrates");
    const protInput = document.getElementById("id_protein");
    const fatInput = document.getElementById("id_fat");
    const calInput = document.getElementById("id_calories");

    if (!foodGroupSelect) return;

    let foodGroupsData = {};

    // API'den Besin Grupları verisini çek
    fetch("/api/food-groups/")
        .then(response => response.json())
        .then(data => {
            foodGroupsData = data.groups;
        })
        .catch(err => console.error("Besin grupları yüklenirken hata:", err));

    foodGroupSelect.addEventListener("change", function () {
        const groupId = this.value;
        if (groupId && foodGroupsData[groupId]) {
            const group = foodGroupsData[groupId];
            
            // Eğer değerler daha önce girilmemişse veya sıfırsa otomatik doldur
            carbInput.value = group.cho;
            protInput.value = group.prot;
            fatInput.value = group.fat;

            // CHO*4 + PROT*4 + YAG*9 şeklinde toplam kaloriyi hesapla
            const calculatedCals = (group.cho * 4) + (group.prot * 4) + (group.fat * 9);
            calInput.value = calculatedCals;
        }
    });

    // Makrolardan biri değişirse kalori bilgisini güncelle (opsiyonel)
    [carbInput, protInput, fatInput].forEach(inp => {
        if(inp) {
            inp.addEventListener("input", function() {
                const c = parseFloat(carbInput.value) || 0;
                const p = parseFloat(protInput.value) || 0;
                const f = parseFloat(fatInput.value) || 0;
                calInput.value = (c * 4) + (p * 4) + (f * 9);
            });
        }
    });
});
