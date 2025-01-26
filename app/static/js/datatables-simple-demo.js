window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }


    const usersTable = document.getElementById('usersTable');
    if (usersTable) {
        new simpleDatatables.DataTable(usersTable);
    }





});


