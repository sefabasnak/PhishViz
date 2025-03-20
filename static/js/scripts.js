// static/js/scripts.js

document.addEventListener('DOMContentLoaded', () => {
  // Modal Açma ve Kapatma Animasyonları
  const modal = document.getElementById('exampleModal');
  const openModalBtn = document.getElementById('openModalBtn');
  const closeModalBtn = document.querySelector('.modal-close');

  if (openModalBtn && modal) {
    openModalBtn.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('show-modal', 'animate__animated', 'animate__zoomIn');
      modal.style.display = 'block';
    });
  }

  if (closeModalBtn && modal) {
    closeModalBtn.addEventListener('click', () => {
      modal.classList.remove('animate__zoomIn');
      modal.classList.add('animate__animated', 'animate__zoomOut');
      setTimeout(() => {
        modal.style.display = 'none';
        modal.classList.remove('animate__animated', 'animate__zoomOut');
      }, 500);
    });
  }

  // Modal dışına tıklayarak kapatma
  window.addEventListener('click', (event) => {
    if (modal && event.target == modal) {
      modal.classList.remove('animate__zoomIn');
      modal.classList.add('animate__animated', 'animate__zoomOut');
      setTimeout(() => {
        modal.style.display = 'none';
        modal.classList.remove('animate__animated', 'animate__zoomOut');
      }, 500);
    }
  });

  // Buton Hover Animasyonları (İsteğe bağlı)
  const buttons = document.querySelectorAll('.btn');

  buttons.forEach(button => {
    button.addEventListener('mouseover', () => {
      button.classList.add('animate__animated', 'animate__pulse');
    });

    button.addEventListener('mouseout', () => {
      button.classList.remove('animate__animated', 'animate__pulse');
    });
  });
});