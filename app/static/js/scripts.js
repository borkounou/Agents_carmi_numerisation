/*!
    * Start Bootstrap - SB Admin v7.0.7 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2023 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }






});



document.addEventListener("DOMContentLoaded", function () {
    const categorySelect = document.getElementById("inputCategory");

    // Restore the selected category from localStorage
    const savedCategory = localStorage.getItem("selectedCategory");
    if (savedCategory) {
        categorySelect.value = savedCategory;
    }

    // Save the selected category to localStorage when it changes
    categorySelect.addEventListener("change", function () {
        localStorage.setItem("selectedCategory", this.value);
    });
});




 // Dynamically update the current year
 document.getElementById("current-year").textContent = new Date().getFullYear();