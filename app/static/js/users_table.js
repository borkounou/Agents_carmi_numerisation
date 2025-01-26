
let userIdToDelete = null;

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





  

