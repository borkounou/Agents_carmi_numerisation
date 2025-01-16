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
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }






});



    document.addEventListener("DOMContentLoaded", () => {
        const deleteButtons = document.querySelectorAll(".delete-user-btn");
        
        deleteButtons.forEach(button => {
            button.addEventListener("click", async () => {
                const username = button.getAttribute("data-user-id");
                
                if (confirm("Are you sure you want to delete this user?")) {
                    try {
                        const response = await fetch(`/admin/delete-user/${username}`, {
                            method: "DELETE",
                            headers: {
                                "Content-Type": "application/json",
                            },
                        });

                        if (response.ok) {
                            alert("User deleted successfully!");
                            button.closest("tr").remove(); // Remove the row from the table
                        } else {
                            const error = await response.json();
                            alert(`Error: ${error.detail}`);
                        }
                    } catch (err) {
                        console.error("Error deleting user:", err);
                        alert("An unexpected error occurred.");
                    }
                }
            });
        });
    });




    async function deleteAgent(agentId) {
        if (confirm("Are you sure you want to delete this agent?")) {
            try {
                const response = await fetch(`/admin/delete-agent/${agentId}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    alert("Agent deleted successfully!");
                    // Remove the row from the table
                    document.querySelector(`[data-user-id="${agentId}"]`).closest('tr').remove();
                } else {
                    const error = await response.json();
                    alert("Error: " + (error.detail || "Unable to delete agent."));
                }
            } catch (error) {
                console.error("Error deleting agent:", error);
                alert("An unexpected error occurred.");
            }
        }
    }



    let agentIdToDelete = null;

    // Open the Delete Modal
    function openDeleteModal(agentId) {
        agentIdToDelete = agentId; // Store the agent ID
        new bootstrap.Modal(document.getElementById("deleteAgentModal")).show();
    }

    // Confirm Delete
    document.getElementById("confirmDeleteButton").addEventListener("click", async function () {
        if (agentIdToDelete !== null) {
            try {
                const response = await fetch(`/admin/delete-agent/${agentIdToDelete}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    alert("Agent deleted successfully!");
                    // Remove the row from the table
                    document.querySelector(`[data-user-id="${agentIdToDelete}"]`).closest('tr').remove();
                } else {
                    const error = await response.json();
                    alert("Error: " + (error.detail || "Unable to delete agent."));
                }
            } catch (error) {
                console.error("Error deleting agent:", error);
                alert("An unexpected error occurred.");
            } finally {
                agentIdToDelete = null; // Reset the agent ID
                bootstrap.Modal.getInstance(document.getElementById("deleteAgentModal")).hide();
            }
        }
    });


    async function openEditModal(agentId) {
        try {
            const response = await fetch(`/admin/get-agent/${agentId}`);
            if (response.ok) {
                const data = await response.json();
                document.getElementById("editAgentId").value = data.id;
                document.getElementById("editNNI").value = data.nni;
                document.getElementById("editFullname").value = data.fullname;
                document.getElementById("editTitleNumber").value = data.title_number;
                document.getElementById("editDateOfBirth").value = data.date_of_birth;
                document.getElementById("editBirthPlace").value = data.birth_place;
                document.getElementById("editCategory").value = data.category;
                document.getElementById("editPhone").value = data.telephone;
                // Populate other fields as necessary
                new bootstrap.Modal(document.getElementById("editAgentModal")).show();
            } else {
                const error = await response.json();
                alert("Error: " + (error.detail || "Failed to fetch agent details."));
            }
        } catch (error) {
            console.error("Error fetching agent details:", error);
            alert("An unexpected error occurred.");
        }
    }

    document.getElementById("editAgentForm").addEventListener("submit", async function (e) {
        e.preventDefault();

        const agentId = document.getElementById("editAgentId").value;
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch(`/admin/edit-agent/${agentId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                alert("Agent updated successfully!");
                window.location.reload(); // Refresh page or update table row dynamically
            } else {
                const error = await response.json();
                alert("Error: " + (error.detail || "Failed to update agent."));
            }
        } catch (error) {
            console.error("Error updating agent:", error);
            alert("An unexpected error occurred.");
        }
    });


    // function openViewModal(pdfPath) {
    //     const viewer = document.getElementById("pdfViewer");
    //     viewer.src = pdfPath; // Set the file path in the iframe
    //     const viewModal = new bootstrap.Modal(document.getElementById("viewPDFModal"));
    //     viewModal.show();
    // } 

    function openViewModal(pdfPath) {
        console.log(pdfPath);
        // Ensure that the path points to the correct URL for serving static files
        const pdfUrl = `/${pdfPath}`;  // Correct URL path to the static file
        console.log(pdfUrl);
        // Set the iframe's source to the correct PDF URL
        const iframe = document.getElementById('pdfViewer');
        iframe.src = pdfUrl;
    
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('viewPDFModal'), {});
        modal.show();
    }
    


    document.addEventListener('DOMContentLoaded', function () {
        function navigateToAgentDetails(agentId) {
            window.location.href = `/admin/detail-agent/${agentId}`;
        }
        window.navigateToAgentDetails = navigateToAgentDetails; // Expose globally if needed
    });

        // Function to open the modal and populate agent details
        function openAgentModal(agentId) {
            // Example: Fetch agent details from the backend based on agentId
            fetch(`/admin/get-agent/${agentId}`)
                .then(response => response.json())
                .then(data => {
                    // Populate modal fields with agent data
                    document.getElementById('agentFullName').textContent = data.fullname;
                    document.getElementById('agentTitleNumber').textContent = data.title_number;
                    document.getElementById('agentNNI').textContent = data.nni;
                    document.getElementById('agentDateOfBirth').textContent = data.date_of_birth;
                    document.getElementById('agentCategory').textContent = data.category;
                    document.getElementById('agentBirthPlace').textContent = data.birth_place;
                    document.getElementById('agentPhone').textContent = data.telephone;
                    document.getElementById('agentPDF').src = data.document_path;  // Assuming the PDF file path is returned
                })
                .catch(error => {
                    console.error('Error fetching agent data:', error);
                });
        }





document.addEventListener('DOMContentLoaded', function () {
    function navAgentDetails(row) {
        // Extract the user ID from the data attribute
        const userId = row.getAttribute('data-user-id');
    
        if (userId) {
            // Navigate to the details page
            window.location.href = `/admin/detail-agent/${userId}`;
        } else {
            console.error("User ID not found on the row.");
        }
    }
            window.navAgentDetails = navAgentDetails; // Expose globally if needed
        });
    
        // JavaScript function to navigate to agent details




 // Fetch total count from the backend
//  fetch('/admin/total-agents').then(response => response.json()).then(data => {
//      // Update the number in the card
//      document.getElementById('totalCount').textContent = data.total_agents;
//  }).catch(error => {
//      console.error('Error fetching total agents:', error);
//      document.getElementById('totalCount').textContent = 'Error';
//  });