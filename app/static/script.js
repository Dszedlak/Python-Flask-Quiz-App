if (document.readyState == 'loading') {
	document.addEventListener('DOMContentLoaded', ready)
} else {
	ready()
}

function ready() {
	var query = new URL(window.location).searchParams.get('search')
	document.getElementById('search').value = query
	document.getElementById('query-output').innerHTML =  'You searched: ' + query.trim()
}

