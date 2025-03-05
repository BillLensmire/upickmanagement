function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updatePlantingDate(planId, plantingDate) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/produceplanner/plan/${planId}/update-planting-date/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
        },
        body: `planting_date=${plantingDate}`,
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Reload the page to show updated dates
            window.location.reload();
        } else {
            alert('Error updating planting date: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error updating planting date: ' + error);
    });
}