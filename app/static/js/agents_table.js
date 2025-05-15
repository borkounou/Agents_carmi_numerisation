let agentIdToDelete = null;

$(document).ready(function () {
    // Initialize category filter (if needed in the future)

    // Initialize DataTable
    const agentTable = $('#mainAgentTable').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: "/admin/agents-table",
            type: "GET",
            data: function (d) {
                d.search_value = d.search.value;
                d.category_filter = $('#categoryFilterDropdown')?.val();  // optional filter
                d.column_filter = JSON.stringify($('#columnFilter')?.val());
                d.column_value = $('#columnSearchValue')?.val();
            }
        },
        columns: [
            { data: "id" },
            { data: "title_number" },
            { data: "nni" },
            { data: "fullname" },
            { data: "date_of_birth" },
            { data: "birth_place" },
            { data: "category" },
            { data: "telephone" },
            { data: "document_path" },
            {
                data: null,
                render: function (data, type, row) {
                    return `
                        <div class="d-flex flex-wrap gap-2 justify-content-center">
                            <button class="btn btn-primary btn-sm table-action-btn" data-user-id="${row.id}" onclick="navigateToAgentDetails(${row.id})">
                                <i class="fas fa-info-circle me-1"></i>Visualiser
                            </button>
                            <button class="btn btn-primary btn-sm table-action-btn" data-user-id="${row.id}" onclick="openEditModal(${row.id})">
                                <i class="fas fa-edit me-1"></i>Modifier
                            </button>
                            <button class="btn btn-danger btn-sm table-action-btn delete-user-btn" data-user-id="${row.id}" onclick="openDeleteModal(${row.id})">
                                <i class="fas fa-trash me-1"></i>Supprimer
                            </button>
                        </div>
                    `;
                }
            }
        ],
        language: {
            search: "Rechercher:",
            lengthMenu: "Afficher _MENU_ entrées par page",
            zeroRecords: "Aucun enregistrement trouvé",
            info: "Affichage de _START_ à _END_ sur _TOTAL_ entrées",
            infoEmpty: "Affichage de 0 à 0 sur 0 entrées",
            infoFiltered: "(filtré à partir de _MAX_ entrées totales)",
            paginate: {
                first: "Premier",
                last: "Dernier",
                next: "Suivant",
                previous: "Précédent"
            }
        }
    });

    // Optional future filters
    $('#categoryFilterDropdown, #columnFilter').change(function () {
        agentTable.ajax.reload();
    });

    $('#columnSearchValue').keyup(function (e) {
        if (e.key === 'Enter') {
            agentTable.ajax.reload();
        }
    });
});


// ==============================
// DELETE
// ==============================

function openDeleteModal(agentId) {
    agentIdToDelete = agentId;
    new bootstrap.Modal(document.getElementById("deleteAgentModal")).show();
}

document.getElementById("confirmDeleteButton").addEventListener("click", async function () {
    if (!agentIdToDelete) return;

    try {
        const response = await fetch(`/admin/delete-agent/${agentIdToDelete}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert("Agent supprimé avec succès!");
            document.querySelector(`[data-user-id="${agentIdToDelete}"]`).closest('tr').remove();
        } else {
            const error = await response.json();
            alert("Erreur: " + (error.detail || "Impossible de supprimer cet agent."));
        }
    } catch (error) {
        console.error("Erreur:", error);
        alert("Une erreur inattendue s'est produite.");
    } finally {
        agentIdToDelete = null;
        bootstrap.Modal.getInstance(document.getElementById("deleteAgentModal")).hide();
    }
});


// ==============================
// EDIT
// ==============================

async function openEditModal(agentId) {
    try {
        const response = await fetch(`/admin/get-agent/${agentId}`);
        if (!response.ok) throw new Error("Erreur serveur");

        const data = await response.json();

        document.getElementById("editAgentId").value = data.id;
        document.getElementById("editNNI").value = data.nni;
        document.getElementById("editFullname").value = data.fullname;
        document.getElementById("editTitleNumber").value = data.title_number;
        document.getElementById("editDateOfBirth").value = data.date_of_birth;
        document.getElementById("editBirthPlace").value = data.birth_place;
        document.getElementById("editPhone").value = data.telephone;

        const categorySelect = document.getElementById('editCategory');
        const savedCategory = data.category;
        const savedOption = Array.from(categorySelect.options).find(option => option.value === savedCategory);

        if (savedOption) {
            categorySelect.removeChild(savedOption);
            categorySelect.insertBefore(savedOption, categorySelect.firstChild);
            categorySelect.value = savedCategory;
        }

        const documentLink = document.getElementById("currentDocumentLink");
        if (data.document_path) {
            documentLink.href = data.document_path;
            documentLink.textContent = "Voir le document actuel";
            documentLink.style.display = "block";
        } else {
            documentLink.style.display = "none";
        }

        new bootstrap.Modal(document.getElementById("editAgentModal")).show();

    } catch (error) {
        console.error("Erreur de chargement:", error);
        alert("Impossible de charger les données de l'agent.");
    }
}

document.getElementById("editAgentForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const agentId = document.getElementById("editAgentId").value;
    const formData = new FormData(e.target);

    try {
        const response = await fetch(`/admin/edit-agent/${agentId}`, {
            method: "PUT",
            body: formData
        });

        if (response.ok) {
            alert("L'agent a été modifié avec succès!");
            window.location.reload();
        } else {
            const error = await response.json();
            alert("Erreur: " + (error.detail || "Erreur lors de la modification"));
        }
    } catch (error) {
        console.error("Erreur de modification:", error);
        alert("Une erreur inattendue s'est produite.");
    }
});


// ==============================
// VIEW
// ==============================

function openViewModal(pdfPath) {
    document.getElementById('pdfViewer').src = `/${pdfPath}`;
    new bootstrap.Modal(document.getElementById('viewPDFModal')).show();
}


// ==============================
// DETAILS
// ==============================

document.addEventListener('DOMContentLoaded', function () {
    window.navigateToAgentDetails = function (agentId) {
        window.location.href = `/admin/detail-agent/${agentId}`;
    };
});

function openAgentModal(agentId) {
    fetch(`/admin/get-agent/${agentId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('agentFullName').textContent = data.fullname;
            document.getElementById('agentTitleNumber').textContent = data.title_number;
            document.getElementById('agentNNI').textContent = data.nni;
            document.getElementById('agentDateOfBirth').textContent = data.date_of_birth;
            document.getElementById('agentCategory').textContent = data.category;
            document.getElementById('agentBirthPlace').textContent = data.birth_place;
            document.getElementById('agentPhone').textContent = data.telephone;
            document.getElementById('agentPDF').src = data.document_path;
        })
        .catch(error => console.error('Erreur de récupération agent:', error));
}
