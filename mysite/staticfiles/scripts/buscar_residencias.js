
const pasajeros = document.querySelector("select[name='pasajeros']");
M.FormSelect.init(pasajeros, {});

const pais = document.querySelector("select[name='pais']");
M.FormSelect.init(pais, {});

const ciudad = document.querySelector("select[name='ciudad']");
M.FormSelect.init(ciudad, {});

hoy = new Date();
const calendario = document.querySelector(".datepicker[name='inicio']");
inicio = M.Datepicker.init(calendario, {
  minDate: hoy, //fecha minima para elegir
  defaultDate: hoy,
  format: "dd/mm/yyyy",
  showDaysInNextAndPreviousMonths: true,
  showMonthAfterYear: true,
  //Traduccion
  i18n: {
    months: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    monthsShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"],
    weekdays: ["Domingo","Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
    weekdaysShort: ["Dom","Lun", "Mar", "Mie", "Jue", "Vie", "Sab"],
    weekdaysAbbrev: ["D","L", "M", "M", "J", "V", "S"]}});


const calendario2 = document.querySelector(".datepicker[name='fin']");
fin = M.Datepicker.init(calendario2, {
  minDate: hoy, //fecha minima para elegir
  defaultDate: hoy,
  format: "dd/mm/yyyy",
  showDaysInNextAndPreviousMonths: true,
  showMonthAfterYear: true,
  //Traduccion
  i18n: {
    months: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    monthsShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"],
    weekdays: ["Domingo","Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
    weekdaysShort: ["Dom","Lun", "Mar", "Mie", "Jue", "Vie", "Sab"],
    weekdaysAbbrev: ["D","L", "M", "M", "J", "V", "S"]}});
