// GARANTE que o JS só roda quando realmente existir um toast na tela
function iniciarToasts() {
  const toasts = document.querySelectorAll('.toast');
  if (!toasts.length) return; // Se não tem toast, não faz nada

  toasts.forEach((toast, i) => {
    setTimeout(() => {
      toast.classList.add('show');

      setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 500);
      }, 3000);

    }, i * 300);
  });
}

// 1) Roda quando o DOM carrega
document.addEventListener('DOMContentLoaded', iniciarToasts);

// 2) Caso o Flask insira flash depois (renderização lenta), usa MutationObserver
const observer = new MutationObserver(() => iniciarToasts());
observer.observe(document.body, { childList: true, subtree: true });
