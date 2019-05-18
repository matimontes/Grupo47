alert("a");
const Elems = document.querySelector('select');
M.FormSelect.init(Elems, {});

const calendario = document.querySelector('.datepicker');
hoy = new Date();
M.Datepicker.init(calendario, {
  minDate: hoy, //fecha minima para elegir
  defaultDate: hoy,
  format: "dd mmmm, yyyy",
  showDaysInNextAndPreviousMonths: true,
  showMonthAfterYear: true,
  //Traduccion
  i18n: {
    months: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    monthsShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"],
    weekdays: ["Domingo","Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
    weekdaysShort: ["Dom","Lun", "Mar", "Mie", "Jue", "Vie", "Sab"],
    weekdaysAbbrev: ["D","L", "M", "M", "J", "V", "S"]}});
