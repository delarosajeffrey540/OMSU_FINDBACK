document.querySelectorAll(".deactivate-user-form").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!window.confirm("Deactivate this account? Its reports and claims will be kept.")) {
      event.preventDefault();
    }
  });
});

document.querySelectorAll(".delete-user-form").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!window.confirm("Move this account to Deleted accounts? You can restore it later.")) {
      event.preventDefault();
    }
  });
});
