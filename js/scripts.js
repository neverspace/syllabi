function texture()
{
	const NTEXTURES = 37;
	let n = parseInt(1 + Math.random() * NTEXTURES);
	let path = 'img/textures/texture' + n + '.png';
	document.body.style.backgroundImage = 'url("' + path + '")';
}

document.body.onload = function() {
	texture();
}
