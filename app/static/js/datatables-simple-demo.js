$(document).ready(function () {
    $('#agentTable').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/admin",  // Endpoint for server-side processing
            "type": "GET",
            "data": function (d) {
                d.search_value = d.search.value;  // Pass search query to the backend
            }
        },
        "columns": [
            { "data": "id" },
            { "data": "title_number" },
            { "data": "nni" },
            { "data": "fullname" },
            { "data": "date_of_birth" },
            { "data": "birth_place" },
            { "data": "category" },
            { "data": "telephone" },
            { "data": "document_path" },
            {
                "data": null,
                "render": function (data, type, row) {
                    return `<button class="btn btn-info btn-sm" onclick="openViewModal('${row.document_path}')">
                                <i class="fas fa-eye me-1"></i>Voir
                            </button>`;
                }
            }
        ],
        "language": {
            "search": "Rechercher:",
            "lengthMenu": "Afficher _MENU_ entrées par page",
            "zeroRecords": "Aucun enregistrement trouvé",
            "info": "Affichage de _START_ à _END_ sur _TOTAL_ entrées",
            "infoEmpty": "Affichage de 0 à 0 sur 0 entrées",
            "infoFiltered": "(filtré à partir de _MAX_ entrées totales)",
            "paginate": {
                "first": "Premier",
                "last": "Dernier",
                "next": "Suivant",
                "previous": "Précédent"
            }
        }
    });
});






$(document).ready(function () {
    $('#manquantTable').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/admin/listes-dossiermanquant",
            "type": "GET",
            "data": function (d) {
                d.search_value = d.search.value;  // Pass search query to the backend
            }
        },
        "columns": [
            { "data": "id" },
            { "data": "title_number" },
            { "data": "fullname" },
            { "data": "category" },
            // No "Action" column
        ],
        "language": {
            "search": "Rechercher:",
            "lengthMenu": "Afficher _MENU_ entrées par page",
            "zeroRecords": "Aucun enregistrement trouvé",
            "info": "Affichage de _START_ à _END_ sur _TOTAL_ entrées",
            "infoEmpty": "Affichage de 0 à 0 sur 0 entrées",
            "infoFiltered": "(filtré à partir de _MAX_ entrées totales)",
            "paginate": {
                "first": "Premier",
                "last": "Dernier",
                "next": "Suivant",
                "previous": "Précédent"
            }
        }
    });
});

function openViewModal(pdfPath) {
    const pdfUrl = `/${pdfPath}`;
    const iframe = document.getElementById('pdfViewer');
    iframe.src = pdfUrl;
    const modal = new bootstrap.Modal(document.getElementById('viewPDFModal'), {});
    modal.show();
}