    
    let dossierManquantIdToDelete = null;



    $(document).ready(function () {
        $('#dossierManquantTable').DataTable({
            "processing": true,
            "serverSide": true,
            "ajax": {
                "url": "/admin/dossier-no-numeriser",  // Endpoint for server-side processing
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
            
                {
                    "data": null,
                    "render": function (data, type, row) {
                        return `
                        <div class="d-flex flex-wrap gap-2 justify-content-center">
                            <button class="btn btn-primary btn-sm table-action-btn" data-user-id="${row.id}" onclick="openEditManquantModal(${row.id})">
                                <i class="fas fa-edit me-1"></i>Modifier
                            </button>
                            <button class="btn btn-danger btn-sm table-action-btn delete-user-btn" data-user-id="${row.id}" onclick="openDeleteManquantModal(${row.id})">
                                <i class="fas fa-trash me-1"></i>Supprimer
                            </button>
                        </div>
                    `;
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

    // Open the Delete Modal
    function openDeleteManquantModal(agentId) {
        dossierManquantIdToDelete = agentId; // Store the agent ID
        new bootstrap.Modal(document.getElementById("deleteManquantModal")).show();
    }
    // Confirm Delete
    document.getElementById("confirmManquantButton").addEventListener("click", async function () {
        if (dossierManquantIdToDelete !== null) {
            try {
                const response = await fetch(`/admin/delete-manquant/${dossierManquantIdToDelete}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    alert("dossier supprimé avec succés!");
                    // Remove the row from the table
                    document.querySelector(`[data-user-id="${dossierManquantIdToDelete}"]`).closest('tr').remove();
                } else {
                    const error = await response.json();
                    alert("Error: " + (error.detail || "Impossible de supprimer ce dossier. Contacter le service d'assistance."));
                }
            } catch (error) {
                console.error("Erreur de suppression de dossier:", error);
                alert("Une erreur inattendue s'est produite.");
            } finally {
                agentIdToDelete = null; // Reset the agent ID
                bootstrap.Modal.getInstance(document.getElementById("deleteManquantModal")).hide();
            }
        }
    });




    async function openEditManquantModal(dossierId) {
        try {
            const response = await fetch(`/admin/get-dossier-manquant/${dossierId}`);
            if (response.ok) {
                const data = await response.json();
                document.getElementById("editManquantId").value = data.id;
                document.getElementById("editManquantTitleNumber").value = data.title_number;
                document.getElementById("editManquantFullname").value = data.fullname;
            // Get the category dropdown element
            const categorySelect = document.getElementById('editManquantCategory');
            const currentOption = document.getElementById('currentCategoryOption');
            // Get the saved category value
            const savedCategory = data.category;
            currentOption.value = savedCategory


            console.log("Saved Category:", savedCategory);

            
            // Convert options to an array for easier manipulation
            const options = Array.from(categorySelect.options);

            console.log("Dropdown Options:", options);

            // Find the saved category option
            const savedOption = options.find(option => option.value === savedCategory);

            if (savedOption) {
                // Remove the saved option from its current position
                categorySelect.removeChild(savedOption);

                // Insert the saved option at the top of the dropdown
                categorySelect.insertBefore(savedOption, categorySelect.firstChild);

                // Set the selected value to the saved category
                categorySelect.value = savedCategory;
            }
            
                new bootstrap.Modal(document.getElementById("editManquantModal")).show();
            } else {
                const error = await response.json();
                alert("Erreur: " + (error.detail || "Erreur pour récupérer les données de l'agent."));
            }
        } catch (error) {
            console.error("Error fetching document details:", error);
            alert("Une erreur s'est produite, reessayer.");
        }
    }

    document.getElementById("editManquantForm").addEventListener("submit", async function (e) {
        e.preventDefault();

        const manquantId = document.getElementById("editManquantId").value;
        const formData = new FormData(e.target);

        try {
            const response = await fetch(`/admin/edit-manquant/${manquantId}`, {
                method: "PUT",
                body: formData
            });

            if (response.ok) {
                alert("Le fichier a été modifié avec succés!");
                window.location.reload(); // Refresh page or update table row dynamically
            } else {
                const error = await response.json();
                alert("Erreur: " + (error.detail || "Erreur pour récupérer les données de fichier."));
            }
        } catch (error) {
            console.error("Error updating agent:", error);
            alert("An unexpected error occurred.");
        }
    });





