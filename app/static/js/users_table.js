let userIdToDelete = null;

// Initialize toast notifications
const toastContainer = document.createElement('div');
toastContainer.id = 'toast-container';
toastContainer.style.position = 'fixed';
toastContainer.style.top = '20px';
toastContainer.style.right = '20px';
toastContainer.style.zIndex = '1100';
document.body.appendChild(toastContainer);

function showToast(type, message) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.role = 'alert';
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.style.marginBottom = '10px';
    
    const toastBody = document.createElement('div');
    toastBody.className = 'd-flex';
    
    const toastContent = document.createElement('div');
    toastContent.className = 'toast-body';
    toastContent.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');
    
    toastBody.appendChild(toastContent);
    toastBody.appendChild(closeButton);
    toast.appendChild(toastBody);
    
    toastContainer.appendChild(toast);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 150);
    }, 5000);
}

$(document).ready(function () {
    initializeUsersTable();
});

function initializeUsersTable() {
    $('#usersTable').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/admin/users-table",
            "type": "GET",
            "data": function (d) {
                d.search_value = d.search.value;
            },
            "error": function(xhr, error, thrown) {
                showToast('danger', 'Erreur lors du chargement des données');
                console.error('DataTables error:', xhr, error, thrown);
            }
        },
        "columns": [
            { "data": "id" },
            { "data": "first_name" },
            { "data": "last_name" },
            { 
                "data": "email",
                "render": function(data) {
                    return `<a href="mailto:${data}">${data}</a>`;
                }
            },
            { "data": "username" },
            { 
                "data": "role",
                "render": function(data) {
                    const badgeClass = data === 'admin' ? 'bg-danger' : 'bg-primary';
                    return `<span class="badge ${badgeClass}">${data}</span>`;
                }
            },
            { 
                "data": "created_at",
                "render": function(data) {
                    return new Date(data).toLocaleDateString('fr-FR');
                }
            },
            {
                "data": null,
                "render": function (data, type, row) {
                    return `
                    <div class="d-flex gap-2">
                        <button class="btn btn-danger btn-sm delete-user-btn" 
                                data-user-id="${row.id}" 
                                onclick="openUserDeleteModal(${row.id})">
                            <i class="fas fa-trash me-1"></i>Supprimer
                        </button>
                    </div>`;
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
        },
        "order": [[0, "desc"]],
        "responsive": true,
        "drawCallback": function(settings) {
            // Add any post-draw operations here
        }
    });
}

function openUserDeleteModal(userId) {
    userIdToDelete = userId;
    new bootstrap.Modal(document.getElementById("deleteUserModal")).show();
}

document.getElementById("confirmUserDeleteButton").addEventListener("click", async function () {
    if (userIdToDelete !== null) {
        try {
            const response = await fetch(`/admin/delete-user/${userIdToDelete}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                showToast('success', 'Utilisateur supprimé avec succès!');
                $('#usersTable').DataTable().ajax.reload();
            } else {
                const error = await response.json();
                showToast('danger', error.detail || "Impossible de supprimer cet utilisateur.");
            }
        } catch (error) {
            console.error("Error deleting user:", error);
            showToast('danger', "Une erreur inattendue s'est produite.");
        } finally {
            userIdToDelete = null;
            bootstrap.Modal.getInstance(document.getElementById("deleteUserModal")).hide();
        }
    }
});


