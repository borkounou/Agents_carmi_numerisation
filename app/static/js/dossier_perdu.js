    
    let dossierPerduIdToDelete = null;
    // Open the Delete Modal
    function openDeletePerduModal(agentId) {
        dossierPerduIdToDelete = agentId; // Store the agent ID
        new bootstrap.Modal(document.getElementById("deletePerduModal")).show();
    }
    // Confirm Delete
    document.getElementById("confirmPerduButton").addEventListener("click", async function () {
        if (dossierPerduIdToDelete !== null) {
            try {
                const response = await fetch(`/admin/delete-perdu/${dossierPerduIdToDelete}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    alert("dossier supprimé avec succés!");
                    // Remove the row from the table
                    document.querySelector(`[data-user-id="${dossierPerduIdToDelete}"]`).closest('tr').remove();
                } else {
                    const error = await response.json();
                    alert("Error: " + (error.detail || "Impossible de supprimer ce dossier. Contacter le service d'assistance."));
                }
            } catch (error) {
                console.error("Erreur de suppression de dossier:", error);
                alert("Une erreur inattendue s'est produite.");
            } finally {
                agentIdToDelete = null; // Reset the agent ID
                bootstrap.Modal.getInstance(document.getElementById("deletePerduModal")).hide();
            }
        }
    });




    async function openEditPerduModal(dossierId) {
        try {
            const response = await fetch(`/admin/get-dossier-perdu/${dossierId}`);
            if (response.ok) {
                const data = await response.json();
                document.getElementById("editPerduId").value = data.id;
                document.getElementById("editPerduTitleNumber").value = data.title_number;
                document.getElementById("editPerduFullname").value = data.fullname;
                document.getElementById("editPerduCategory").value = data.category;
                document.getElementById("editPerduFolder").value = data.folder;
            
                new bootstrap.Modal(document.getElementById("editPerduModal")).show();
            } else {
                const error = await response.json();
                alert("Erreur: " + (error.detail || "Erreur pour récupérer les données de l'agent."));
            }
        } catch (error) {
            console.error("Error fetching document details:", error);
            alert("Une erreur s'est produite, reessayer.");
        }
    }

    document.getElementById("editPerduForm").addEventListener("submit", async function (e) {
        e.preventDefault();

        const perduId = document.getElementById("editPerduId").value;
        const formData = new FormData(e.target);

        try {
            const response = await fetch(`/admin/edit-perdu/${perduId}`, {
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
