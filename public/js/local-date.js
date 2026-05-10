(() => {
  const dateInputs = document.querySelectorAll("input[type='date'][data-local-default-date='true']");

  if (!dateInputs.length) {
    return;
  }

  // The default entry date is set in the browser so the phone's local calendar day wins over server UTC.
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const localDate = `${year}-${month}-${day}`;

  dateInputs.forEach((input) => {
    input.value = localDate;
  });
})();
