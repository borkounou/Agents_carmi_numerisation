
let userIdToDelete = null;


$(document).ready(function () {
    $('#usersTable').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/admin/users-table",  // Endpoint for server-side processing
            "type": "GET",
            "data": function (d) {
                d.search_value = d.search.value;  // Pass search query to the backend
            }
        
        },
        "columns": [
            { "data": "id" },
            { "data": "first_name" },
            { "data": "last_name" },
            { "data": "email" },
            { "data": "username" },
            { "data": "role" },
            { "data": "created_at" },
            {
                "data": null,
                "render": function (data, type, row) {
                    return `<button class="btn btn-danger btn-sm table-action-btn delete-user-btn" data-user-id="${row.id}" onclick="openUserDeleteModal(${row.id})">
                                <i class="fas fa-trash me-1"></i>Supprimer
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



function openUserDeleteModal(userId) {
    userIdToDelete = userId; // Store the agent ID
    new bootstrap.Modal(document.getElementById("deleteUserModal")).show();
}


document.getElementById("confirmUserDeleteButton").addEventListener("click", async function () {
        if (userIdToDelete !== null) {
            try {
                const response = await fetch(`/admin/delete-user/${userIdToDelete}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    alert("Utilisateur supprimé avec succés!");
                    // Remove the row from the table
                    document.querySelector(`[data-user-id="${userIdToDelete}"]`).closest('tr').remove();
                } else {
                    const error = await response.json();
                    alert("Error: " + (error.detail || "Impossible de supprimer cet utilisateur."));
                }
            } catch (error) {
                console.error("Error deleting agent:", error);
                alert("An unexpected error occurred.");
            } finally {
                agentIdToDelete = null; // Reset the agent ID
                bootstrap.Modal.getInstance(document.getElementById("deleteUserModal")).hide();
            }
        }
    });





  

