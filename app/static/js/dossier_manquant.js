    
    let dossierManquantIdToDelete = null;
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
                document.getElementById("editManquantCategory").value = data.category;
               
            
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
