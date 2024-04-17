const btn = document.getElementById('btn');

// ✅ Change button text on click
btn.addEventListener('click', function handleClick() {
  btn.textContent = 'Button clicked';
});

/**
 * ✅ If you need to change the button's inner HTML use:
 *  - `innerHTML` instead of `textContent`
 */
