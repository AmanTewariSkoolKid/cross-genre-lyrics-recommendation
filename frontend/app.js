document.addEventListener('DOMContentLoaded', () => {
	// Tab logic
	const tabs = document.querySelectorAll('.tab-btn');
	tabs.forEach(btn => btn.addEventListener('click', () => {
		tabs.forEach(t => t.classList.remove('active'));
		btn.classList.add('active');
		tabs.forEach(t => t.setAttribute('aria-selected', t === btn ? 'true' : 'false'));
		const target = btn.dataset.target;
		document.querySelectorAll('.tab-panel').forEach(panel => {
			if (panel.id === target) panel.removeAttribute('hidden'); else panel.setAttribute('hidden', '');
		});
	}));

	// Wire up search buttons
	document.getElementById('titleSearch').addEventListener('click', recommendByTitle);
	document.getElementById('lyricsSearch').addEventListener('click', recommendByLyrics);

	// Keep common actions one-step fast with Enter.
	document.getElementById('songTitle').addEventListener('keydown', (event) => {
		if (event.key === 'Enter') {
			event.preventDefault();
			recommendByTitle();
		}
	});

	document.getElementById('lyricsInput').addEventListener('keydown', (event) => {
		if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
			event.preventDefault();
			recommendByLyrics();
		}
	});
});

function showToast(text, timeout = 3000){
	const container = document.getElementById('toast-container');
	const t = document.createElement('div');
	t.className = 'toast-msg';
	t.textContent = text;
	container.appendChild(t);
	setTimeout(()=>{t.style.opacity = '0'; setTimeout(()=>t.remove(),300)}, timeout);
}

function recommendByTitle(){
	const title = document.getElementById('songTitle').value.trim();
	if(!title){ showToast('Please enter a song title'); return; }

	const container = document.getElementById('titleResults');
	showLoader(container);

	// TODO: replace simulated fetch with real backend call
	setTimeout(()=>{
		const results = [
			{title:'Shape of You', artist:'Ed Sheeran'},
			{title:'Someone Like You', artist:'Adele'},
			{title:'Blinding Lights', artist:'The Weeknd'},
			{title:'Levitating', artist:'Dua Lipa'},
			{title:'Stay', artist:'The Kid LAROI'}
		];
		displayResults(results, container);
	}, 700);
}

function recommendByLyrics(){
	const lyrics = document.getElementById('lyricsInput').value.trim();
	if(!lyrics){ showToast('Please paste lyrics'); return; }
	const words = lyrics.split(/\s+/).filter(Boolean).length;
	if(words < 10){ showToast('Please provide a longer lyrics sample'); return; }

	const container = document.getElementById('lyricsResults');
	showLoader(container);

	// TODO: replace with actual API call to analyze lyrics
	setTimeout(()=>{
		const results = [
			{title:'Fix You', artist:'Coldplay'},
			{title:'Let Her Go', artist:'Passenger'},
			{title:'Halo', artist:'Beyoncé'},
			{title:'Rolling in the Deep', artist:'Adele'}
		];
		displayResults(results, container);
	}, 900);
}

function showLoader(container){
	container.innerHTML = '';
	const row = document.createElement('div');
	row.className = 'row g-3';
	for(let i=0;i<4;i++){
		const col = document.createElement('div');
		col.className = 'col-12 col-md-6 col-xl-4';
		col.innerHTML = '<div class="result-card" style="opacity:0.55;"><div style="height:2.25rem;background:rgba(35,76,106,0.12);border-radius:0.4rem"></div></div>';
		row.appendChild(col);
	}
	container.appendChild(row);
}

function displayResults(data, container){
	if(typeof container === 'string') container = document.getElementById(container);
	container.innerHTML = '';
	data.forEach(item => {
		const col = document.createElement('div');
		col.className = 'col-12 col-md-6 col-xl-4';

		const card = document.createElement('div');
		card.className = 'result-card';
		card.tabIndex = 0;
		card.innerHTML = `
			<div class="result-meta">
				<div class="result-art">♪</div>
				<div>
					<div class="result-title">${escapeHtml(item.title)}</div>
					<div class="result-subtitle">${escapeHtml(item.artist)}</div>
				</div>
			</div>`;

		card.addEventListener('click', ()=> showToast(`${item.title} - ${item.artist}`));
		card.addEventListener('keydown', (event) => {
			if (event.key === 'Enter') showToast(`${item.title} - ${item.artist}`);
		});

		col.appendChild(card);
		container.appendChild(col);
	});
}

function escapeHtml(str){
	return (str+'').replace(/[&<>\"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}