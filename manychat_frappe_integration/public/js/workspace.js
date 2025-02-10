$(document).ready(function() {
    console.log("Initializing custom search functionality");

    setTimeout(function() {
        // Hide the original search elements
        $('.search-bar').hide();
        $('.navbar-center').hide();

        // Create and add the custom search bar with button
        $('.search-bar').after(`
            <div class="custom-search-container" style="display: flex; align-items: center; gap: 8px;">
                <div class="input-group">
                    <input type="text" 
                           class="form-control custom-search-input" 
                           placeholder="Search leads..."
                           style="height: 28px; width: 200px;">
                    <div class="input-group-append">
                        <button class="btn btn-primary btn-sm" 
                                onclick="leadSearchByNumber()">
                            <span class="hidden-xs">Search</span>
                        </button>
                    </div>
                </div>
            </div>
        `);

        // Add event listener for Enter key
        $('.custom-search-input').on('keypress', function(e) {
            if (e.which === 13) { // Enter key
                leadSearchByNumber();
            }
        });
    }, 1000);
});

// Define the search function
function leadSearchByNumber() {
    const mobileNo = $('.custom-search-input').val().trim();
    console.log("number is", mobileNo);
    
    if (!mobileNo) {
        frappe.throw('Please enter a mobile number');
        return;
    }

    // Perform the search without freezing the UI
    frappe.call({
        method: 'manychat_frappe_integration.manychat_frappe_integration.api.search_leads.search_lead_by_mobile',
        args: {
            mobile_no: mobileNo
        },
        callback: function(r) {
            if (r.message) {
                showLeadDialog(r.message);
            } else {
                frappe.show_alert({
                    message: 'No lead found with this mobile number',
                    indicator: 'red'
                });
            }
        }
    });
}

function showLeadDialog(leadName) {
    // Create a new dialog
    const d = new frappe.ui.Dialog({
        title: 'Lead Found',
        fields: [
            {
                fieldname: 'lead_link',
                fieldtype: 'HTML',
                options: `
                    <div style="padding: 10px 0;">
                        <p>Click below to view the lead:</p>
                        <a href="/app/lead/${leadName}"
                           class="btn btn-primary btn-sm" 
                           onclick="cur_dialog.hide()">
                            View Lead: ${leadName}
                        </a>
                    </div>
                `
            }
        ],
        primary_action_label: 'Close',
        primary_action: () => {
            d.hide();
        }
    });

    d.show();
}

// Add custom styles
frappe.dom.set_style(`
    .search-bar, .navbar-center {
        display: none !important;
    }
    
    .custom-search-container {
        padding: 0 10px;
    }
    
    .custom-search-input {
        border-radius: 4px 0 0 4px;
    }
    
    .custom-search-container .btn {
        border-radius: 0 4px 4px 0;
        height: 28px;
        display: flex;
        align-items: center;
    }
`);