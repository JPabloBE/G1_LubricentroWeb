/**
 * i18n.js — ES / EN language toggle for Lubricentro client portal
 * Loads in <head>; window.i18n.t() is available immediately.
 * DOM injection (toggle button) waits for DOMContentLoaded.
 */
(function () {
  "use strict";

  // ─────────────────────────────────────────────────────────────
  // DICTIONARY
  // ─────────────────────────────────────────────────────────────
  var T = {
    es: {
      // Topbar info chips
      topbar_call:       "¡Llámanos ahora!",
      topbar_hours:      "Horario de atención",
      topbar_find:       "Encuéntranos",
      topbar_hours_val:  "Lun-Sáb : 09:00-19:00",
      mob_hours:         "Lun-Sáb 9-19h",
      mob_loc:           "Montecillos",

      // Navigation
      nav_home:          "Inicio",
      nav_about:         "Nosotros",
      nav_services:      "Servicios",
      nav_contact:       "Contacto",
      nav_portal:        "Portal",
      nav_client_portal: "Portal Cliente",
      nav_staff:         "Acceso Staff",
      nav_login_btn:     "Iniciar sesión",
      nav_dashboard:     "Dashboard",
      nav_my_appts:      "Mis Citas",
      nav_my_cars:       "Mis Autos",
      nav_orders:        "Órdenes",
      nav_logout:        "Cerrar sesión",
      nav_menu:          "Menú",
      nav_close_menu:    "Cerrar menú",
      notif_title:       "Recordatorios",
      notif_empty:       "Sin recordatorios pendientes",
      btn_seen:          "Visto",

      // Index hero
      hero_title:        "Tu aliado de confianza para todo lo que tu vehículo necesita",
      hero_sub:          "Desde mantenimiento rutinario hasta reparaciones mayores, estamos listos para ayudarte.",
      hero_cta:          "Agendá tu cita",

      // About
      about_eyebrow:     "Quiénes somos",
      about_title:       "Expertos en el cuidado de tu vehículo",
      about_p1:          "Somos un lubricentro con más de 10 años de experiencia brindando servicios automotrices de alta calidad. Nuestro equipo de técnicos certificados trabaja con los mejores estándares para garantizar la seguridad y el rendimiento de tu vehículo.",
      about_p2:          "Usamos equipos de diagnóstico de última generación y productos de primera línea para ofrecerte un servicio confiable, rápido y a precios accesibles.",
      about_cta:         "Descubrir más",

      // Trust checklist
      trust_eyebrow:     "Profesionalismo garantizado",
      trust_title:       "Confiá tu vehículo a nuestros técnicos",
      trust_desc:        "Nuestros profesionales están capacitados para trabajar con todo tipo de vehículos, desde autos compactos hasta camionetas y SUVs.",
      check_certified:   "Técnicos certificados",
      check_warranty:    "Garantía en repuestos",
      check_diagnosis:   "Diagnóstico preciso",
      check_personal:    "Atención personalizada",
      check_equipment:   "Equipos de última generación",
      check_quote:       "Presupuesto sin costo",
      check_punctual:    "Puntualidad garantizada",
      check_transparent: "Transparencia total",

      // Stats
      stat_clients:      "Clientes satisfechos",
      stat_vehicles:     "Vehículos atendidos",
      stat_satisfaction: "Satisfacción",
      stat_years:        "Años de experiencia",

      // Services
      svc_eyebrow:       "Lo que ofrecemos",
      svc_title:         "Nuestros Servicios",
      svc_desc:          "Ofrecemos soluciones integrales para el mantenimiento y la reparación de tu vehículo. Desde servicios preventivos hasta correcciones complejas.",
      svc_learn_more:    "Saber más",
      svc1_title:        "Revisión General",
      svc1_desc:         "Evaluación completa del motor, niveles de líquidos, sistema de frenos, suspensión, dirección, luces y neumáticos.",
      svc2_title:        "Cambio de Aceite y Filtro",
      svc2_desc:         "Sustitución del aceite del motor y filtro de aceite. Incluye revisión de nivel de líquidos y presión de neumáticos.",
      svc3_title:        "Alineación y Balanceo",
      svc3_desc:         "Ajuste de geometría de ruedas y balanceo de neumáticos para una conducción segura y mayor vida útil de las llantas.",
      svc4_title:        "Servicio de Frenos",
      svc4_desc:         "Inspección y reemplazo de pastillas, discos y líquido de frenos. Incluye prueba de funcionamiento en pista de seguridad.",
      svc5_title:        "Diagnóstico Computarizado",
      svc5_desc:         "Análisis electrónico del sistema OBD para detectar fallas en motor, transmisión, ABS y airbags con equipos de última generación.",
      svc6_title:        "Mano de Obra Especializada",
      svc6_desc:         "Intervenciones técnicas especializadas por mecánicos certificados. Presupuesto personalizado según la necesidad de tu vehículo.",

      // Why us
      why_eyebrow:       "Nuestras ventajas",
      why_title:         "¿Por qué elegirnos?",
      why_desc:          "Nos diferenciamos por la calidad, rapidez y transparencia en cada servicio. Tu tranquilidad es nuestra prioridad.",
      why_warranty_t:    "Garantía en todos los servicios",
      why_warranty_d:    "Respaldamos nuestro trabajo con garantía escrita en repuestos y mano de obra.",
      why_speed_t:       "Servicio rápido y sin demoras",
      why_speed_d:       "Respetamos tu tiempo. La mayoría de servicios se completan el mismo día de la cita.",
      why_comm_t:        "Comunicación transparente",
      why_comm_d:        "Te informamos de cada paso antes de realizar el trabajo. Sin sorpresas en el presupuesto final.",
      why_badge:         "Vehículos atendidos",

      // CTA banner
      cta_title:         "¿Listo para darle a tu vehículo el mantenimiento que merece?",
      cta_sub:           "Agendá tu cita en minutos y te atendemos el mismo día.",
      cta_button:        "Agendar cita ahora",

      // News
      news_eyebrow:      "Blog & Consejos",
      news_title:        "Noticias y Tips para tu Auto",
      news_see_all:      "Ver todos",

      // Footer
      footer_nav:        "Navegación",
      footer_contact:    "Contacto",
      footer_hours_f:    "Lun – Sáb: 09:00 – 19:00",
      footer_copy:       "© 2026 Lubricentro Montecillos. Todos los derechos reservados.",

      // Auth page
      auth_eyebrow:      "Tu portal personal",
      auth_benefit_title:"Tu taller, siempre a mano.",
      auth_benefit_sub:  "Creá tu cuenta y gestioná todo desde un solo lugar.",
      b1_title:          "Seguimiento en tiempo real",
      b1_desc:           "Conocé el estado de tu vehículo en cada etapa del servicio.",
      b2_title:          "Agendá tu cita",
      b2_desc:           "Reservá turnos online, sin llamadas ni esperas.",
      b3_title:          "Avisos de mantenimiento",
      b3_desc:           "Recordatorios automáticos antes de que venza tu próximo servicio.",
      b4_title:          "Promociones exclusivas",
      b4_desc:           "Descuentos y beneficios especiales solo para clientes registrados.",
      auth_form_eyebrow: "Acceso",
      auth_form_title:   "Bienvenido/a",
      auth_form_sub:     "Accedé a tu portal o creá una cuenta nueva.",
      tab_login:         "Iniciar sesión",
      tab_register:      "Crear cuenta",
      lbl_email:         "Correo electrónico",
      ph_email:          "tucorreo@email.com",
      lbl_password:      "Contraseña",
      lbl_confirm:       "Confirmar",
      ph_confirm:        "Repetí",
      hint_password:     "Mín. 8 caracteres",
      btn_login:         "Entrar",
      lbl_name:          "Nombre completo",
      ph_name:           "Juan Pérez",
      lbl_phone:         "Teléfono (opc.)",
      ph_phone:          "+(506) 0000-0000",
      btn_register:      "Crear cuenta",
      is_admin_text:     "¿Sos admin/staff?",
      is_admin_link:     "Ir al acceso staff",
      back_home:         "Volver al inicio",

      // Client portal common
      client_portal:     "Portal Cliente",
      greeting_prefix:   "Bienvenido/a,",

      // Dashboard
      dash_active_title: "Tus citas activas",
      empty_no_active:   "No tenés citas activas en este momento",
      empty_book_cta:    "Agendar una cita",
      btn_book_new:      "Agendar nueva cita",
      btn_my_cars:       "Mis autos",

      // Appointments page
      page_appts_eyebrow:"Mis Citas",
      page_appts_title:  "Gestión de Citas",
      page_appts_sub:    "Agendá nuevas citas y revisá el estado de las existentes.",
      form_new_appt:     "Nueva cita",
      lbl_vehicle:       "Vehículo",
      opt_new_vehicle:   "+ Registrar vehículo nuevo",
      new_veh_panel:     "Datos del vehículo nuevo",
      lbl_plate:         "Placa",
      ph_plate:          "Ej: ABC-123",
      lbl_make:          "Marca",
      ph_make:           "Toyota",
      lbl_model:         "Modelo",
      ph_model:          "Corolla",
      lbl_year:          "Año",
      ph_year:           "2024",
      lbl_color:         "Color",
      ph_color:          "Blanco",
      lbl_service:       "Servicio",
      lbl_slot:          "Horario disponible",
      hint_slots:        "Solo aparecen horarios con cupo disponible.",
      lbl_req_work:      "Trabajo solicitado (opcional)",
      ph_req_work:       "Ej: cambio de aceite, revisión de frenos...",
      lbl_notes:         "Notas adicionales (opcional)",
      ph_notes:          "Cualquier detalle extra.",
      btn_confirm_appt:  "Confirmar cita",
      appts_active_title:"Citas activas",
      filter_all:        "Todas",
      filter_unconfirmed:"Sin confirmar",
      filter_confirmed:  "Confirmada",
      filter_in_progress:"En progreso",
      filter_ready:      "Listo para retirar",
      btn_refresh:       "Actualizar",
      appts_past_title:  "Citas anteriores",
      filter_completed:  "Completada",
      filter_cancelled:  "Cancelada",
      empty_active_all:  "No tenés citas activas en este momento.",
      empty_active_flt:  "No hay citas activas con este estado.",
      empty_past_all:    "No tenés citas anteriores.",
      empty_past_flt:    "No hay citas anteriores con este estado.",

      // Status badges
      status_unconfirmed:"Sin confirmar",
      status_confirmed:  "Confirmada",
      status_in_progress:"En progreso",
      status_ready:      "Listo para retirar",
      status_completed:  "Completada",
      status_cancelled:  "Cancelada",

      // WO progress descriptions
      wo_received:       "Recibimos tu vehículo",
      wo_diagnosing:     "Revisando tu vehículo",
      wo_awaiting_auth:  "Esperando tu autorización",
      wo_authorized:     "Listo para iniciar reparación",
      wo_in_progress:    "Trabajando en tu vehículo",
      wo_waiting_parts:  "Esperando repuestos",
      wo_ready:          "¡Listo para retirar!",
      wo_pending_conf:   "Pendiente de confirmación",
      wo_being_attended: "Tu vehículo está siendo atendido",
      wo_appt_confirmed: "Tu cita está confirmada",

      // Card actions
      btn_view_detail:   "Ver detalle",
      btn_cancel:        "Cancelar",

      // Vehicles page
      page_veh_eyebrow:  "Mis Autos",
      page_veh_title:    "Mis Vehículos",
      page_veh_sub:      "Todos los vehículos asociados a tu cuenta.",
      veh_registered:    "Vehículos registrados",
      btn_add_vehicle:   "Agregar vehículo",
      btn_reload:        "Recargar",
      empty_no_vehicles: "No tenés vehículos registrados en tu cuenta.",
      modal_add_veh_title:"Agregar vehículo",
      modal_add_veh_sub: "Registrá un nuevo auto en tu cuenta",
      ph_plate_veh:      "Ej: ABC123",
      ph_make_veh:       "Ej: Toyota",
      ph_model_veh:      "Ej: Corolla",
      ph_year_veh:       "Ej: 2020",
      ph_color_veh:      "Ej: Plateado",
      lbl_image_url:     "URL de imagen (opc.)",
      ph_image_url:      "https://...",
      btn_save_vehicle:  "Guardar vehículo",

      // Appointment detail
      back_to_appts:     "Volver a mis citas",
      wo_section_title:  "Estado de tu vehículo",
      step_received:     "Recibido",
      step_diagnostic:   "Diagnóstico",
      step_repair:       "Reparación",
      step_ready:        "Listo",
      wo_detail_title:   "Tu orden de trabajo",
      wo_symptoms:       "Síntomas reportados",
      wo_diagnosis_f:    "Diagnóstico del taller",
      wo_notes_f:        "Notas",
      wo_services_s:     "Servicios",
      wo_products_s:     "Productos",
      wo_col_desc:       "Descripción",
      wo_col_qty:        "Cant.",
      wo_col_unit:       "Unit.",
      wo_col_total:      "Total",
      wo_no_services:    "No hay servicios registrados.",
      wo_computed_total: "Total calculado",
      wo_no_info:        "Aún no hay información registrada en esta orden.",
      sidebar_workshop:  "Mensaje del taller",
      sidebar_appt_det:  "Detalles de la cita",
      sidebar_appt_date: "Fecha de la cita",
      sidebar_service:   "Servicio",
      sidebar_req_work:  "Trabajo solicitado",
      sidebar_notes:     "Notas",
      sidebar_no_wo:     "Tu cita está confirmada",
      sidebar_no_wo_d:   "El taller abrirá la orden de trabajo al recibir tu vehículo.",
      btn_cancel_appt:   "Cancelar esta cita",

      // Work orders page
      page_wo_eyebrow:   "Historial",
      page_wo_title:     "Mis Órdenes de Trabajo",
      page_wo_sub:       "Revisá el detalle de todos los servicios realizados en tu vehículo.",
      wo_registered:     "Órdenes registradas",
      btn_expand:        "Ver detalles",
      wo_subtotal_svc:   "Subtotal servicios",
      wo_subtotal_prod:  "Subtotal productos",
      wo_opened:         "Abierta",
      wo_closed_lbl:     "Cerrada",
      col_qty:           "Cant",
      col_unit:          "Unit",
      wo_no_products:    "No hay productos registrados.",
      empty_no_orders:   "No tenés órdenes de trabajo registradas.",

      // WO status labels
      wo_status_open:    "Abierta",
      wo_status_diag:    "En diagnóstico",
      wo_status_prog:    "En progreso",
      wo_status_parts:   "Esperando piezas",
      wo_status_auth:    "Pendiente de autorización",
      wo_status_authd:   "Autorizada",
      wo_status_ready:   "Lista para entregar",
      wo_status_closed:  "Cerrada",
      wo_status_done:    "Completada",
      wo_status_cancel:  "Cancelada",

      // Vehicle history
      back_to_vehicles:  "Mis Autos",
      veh_file_label:    "Expediente del vehículo",
      history_title:     "Historial de servicios",
      btn_refresh_hist:  "Actualizar",
      empty_no_history:  "No hay servicios registrados para este vehículo todavía.",
      svc_singular:      "servicio",
      svc_plural:        "servicios",
      prod_singular:     "producto",
      prod_plural:       "productos",
      wo_diagnosis_lbl:  "Diagnóstico",
      wo_no_entries:     "Sin servicios ni productos registrados.",

      // Profile modal
      profile_title:     "Mi perfil",
      profile_sub:       "Revisá y editá tus datos personales",
      profile_name:      "Nombre completo",
      profile_email:     "Correo electrónico",
      profile_phone:     "Teléfono (opc.)",
      btn_save_changes:  "Guardar cambios",
    },

    en: {
      // Topbar info chips
      topbar_call:       "Call us now!",
      topbar_hours:      "Business hours",
      topbar_find:       "Find us",
      topbar_hours_val:  "Mon-Sat : 09:00-19:00",
      mob_hours:         "Mon-Sat 9am-7pm",
      mob_loc:           "Montecillos",

      // Navigation
      nav_home:          "Home",
      nav_about:         "About us",
      nav_services:      "Services",
      nav_contact:       "Contact",
      nav_portal:        "Portal",
      nav_client_portal: "Client Portal",
      nav_staff:         "Staff Access",
      nav_login_btn:     "Sign in",
      nav_dashboard:     "Dashboard",
      nav_my_appts:      "My Appointments",
      nav_my_cars:       "My Vehicles",
      nav_orders:        "Orders",
      nav_logout:        "Sign out",
      nav_menu:          "Menu",
      nav_close_menu:    "Close menu",
      notif_title:       "Reminders",
      notif_empty:       "No pending reminders",
      btn_seen:          "Seen",

      // Index hero
      hero_title:        "Your trusted partner for all your vehicle needs",
      hero_sub:          "From routine maintenance to major repairs, we're ready to help you.",
      hero_cta:          "Book your appointment",

      // About
      about_eyebrow:     "Who we are",
      about_title:       "Vehicle care experts",
      about_p1:          "We are a lubrication center with over 10 years of experience providing high-quality automotive services. Our team of certified technicians works with the highest standards to ensure your vehicle's safety and performance.",
      about_p2:          "We use state-of-the-art diagnostic equipment and premium products to offer you reliable, fast service at affordable prices.",
      about_cta:         "Learn more",

      // Trust checklist
      trust_eyebrow:     "Guaranteed professionalism",
      trust_title:       "Trust your vehicle to our technicians",
      trust_desc:        "Our professionals are trained to work with all types of vehicles, from compact cars to trucks and SUVs.",
      check_certified:   "Certified technicians",
      check_warranty:    "Parts warranty",
      check_diagnosis:   "Precise diagnosis",
      check_personal:    "Personalized attention",
      check_equipment:   "State-of-the-art equipment",
      check_quote:       "Free quote",
      check_punctual:    "Guaranteed punctuality",
      check_transparent: "Total transparency",

      // Stats
      stat_clients:      "Satisfied customers",
      stat_vehicles:     "Vehicles serviced",
      stat_satisfaction: "Satisfaction",
      stat_years:        "Years of experience",

      // Services
      svc_eyebrow:       "What we offer",
      svc_title:         "Our Services",
      svc_desc:          "We offer comprehensive solutions for vehicle maintenance and repair. From preventive services to complex fixes.",
      svc_learn_more:    "Learn more",
      svc1_title:        "General Inspection",
      svc1_desc:         "Complete engine evaluation, fluid levels, brake system, suspension, steering, lights, and tires.",
      svc2_title:        "Oil and Filter Change",
      svc2_desc:         "Engine oil and oil filter replacement. Includes fluid level check and tire pressure.",
      svc3_title:        "Alignment and Balancing",
      svc3_desc:         "Wheel geometry adjustment and tire balancing for safe driving and extended tire life.",
      svc4_title:        "Brake Service",
      svc4_desc:         "Brake pad, disc, and fluid inspection and replacement. Includes safety track testing.",
      svc5_title:        "Computerized Diagnosis",
      svc5_desc:         "Electronic OBD system analysis to detect engine, transmission, ABS, and airbag faults.",
      svc6_title:        "Specialized Labor",
      svc6_desc:         "Specialized technical work by certified mechanics. Custom pricing based on your vehicle's needs.",

      // Why us
      why_eyebrow:       "Our advantages",
      why_title:         "Why choose us?",
      why_desc:          "We stand out for quality, speed, and transparency in every service. Your peace of mind is our priority.",
      why_warranty_t:    "Warranty on all services",
      why_warranty_d:    "We back our work with written warranty on parts and labor.",
      why_speed_t:       "Fast, no-hassle service",
      why_speed_d:       "We respect your time. Most services are completed same-day.",
      why_comm_t:        "Transparent communication",
      why_comm_d:        "We inform you of every step before doing the work. No surprises in the final quote.",
      why_badge:         "Vehicles serviced",

      // CTA banner
      cta_title:         "Ready to give your vehicle the maintenance it deserves?",
      cta_sub:           "Book your appointment in minutes and we'll serve you the same day.",
      cta_button:        "Book appointment now",

      // News
      news_eyebrow:      "Blog & Tips",
      news_title:        "News and tips for your car",
      news_see_all:      "See all",

      // Footer
      footer_nav:        "Navigation",
      footer_contact:    "Contact",
      footer_hours_f:    "Mon – Sat: 09:00 – 19:00",
      footer_copy:       "© 2026 Lubricentro Montecillos. All rights reserved.",

      // Auth page
      auth_eyebrow:      "Your personal portal",
      auth_benefit_title:"Your workshop, always at hand.",
      auth_benefit_sub:  "Create your account and manage everything in one place.",
      b1_title:          "Real-time tracking",
      b1_desc:           "Know your vehicle's status at every service stage.",
      b2_title:          "Book your appointment",
      b2_desc:           "Reserve slots online, no calls or waiting.",
      b3_title:          "Maintenance reminders",
      b3_desc:           "Automatic reminders before your next service is due.",
      b4_title:          "Exclusive promotions",
      b4_desc:           "Special discounts and benefits for registered customers only.",
      auth_form_eyebrow: "Access",
      auth_form_title:   "Welcome",
      auth_form_sub:     "Access your portal or create a new account.",
      tab_login:         "Sign in",
      tab_register:      "Create account",
      lbl_email:         "Email address",
      ph_email:          "youremail@email.com",
      lbl_password:      "Password",
      lbl_confirm:       "Confirm",
      ph_confirm:        "Repeat",
      hint_password:     "Min. 8 characters",
      btn_login:         "Sign in",
      lbl_name:          "Full name",
      ph_name:           "John Doe",
      lbl_phone:         "Phone (optional)",
      ph_phone:          "+(506) 0000-0000",
      btn_register:      "Create account",
      is_admin_text:     "Are you admin/staff?",
      is_admin_link:     "Go to staff access",
      back_home:         "Back to home",

      // Client portal common
      client_portal:     "Client Portal",
      greeting_prefix:   "Welcome,",

      // Dashboard
      dash_active_title: "Your active appointments",
      empty_no_active:   "You don't have active appointments at the moment",
      empty_book_cta:    "Book an appointment",
      btn_book_new:      "Book new appointment",
      btn_my_cars:       "My vehicles",

      // Appointments page
      page_appts_eyebrow:"My Appointments",
      page_appts_title:  "Appointment Management",
      page_appts_sub:    "Book new appointments and review existing ones.",
      form_new_appt:     "New appointment",
      lbl_vehicle:       "Vehicle",
      opt_new_vehicle:   "+ Register new vehicle",
      new_veh_panel:     "New vehicle details",
      lbl_plate:         "License plate",
      ph_plate:          "E.g.: ABC-123",
      lbl_make:          "Brand",
      ph_make:           "Toyota",
      lbl_model:         "Model",
      ph_model:          "Corolla",
      lbl_year:          "Year",
      ph_year:           "2024",
      lbl_color:         "Color",
      ph_color:          "White",
      lbl_service:       "Service",
      lbl_slot:          "Available time slot",
      hint_slots:        "Only time slots with available capacity are shown.",
      lbl_req_work:      "Requested work (optional)",
      ph_req_work:       "E.g.: oil change, brake inspection...",
      lbl_notes:         "Additional notes (optional)",
      ph_notes:          "Any extra details.",
      btn_confirm_appt:  "Confirm appointment",
      appts_active_title:"Active appointments",
      filter_all:        "All",
      filter_unconfirmed:"Unconfirmed",
      filter_confirmed:  "Confirmed",
      filter_in_progress:"In progress",
      filter_ready:      "Ready for pickup",
      btn_refresh:       "Refresh",
      appts_past_title:  "Past appointments",
      filter_completed:  "Completed",
      filter_cancelled:  "Cancelled",
      empty_active_all:  "You don't have active appointments.",
      empty_active_flt:  "No active appointments with this status.",
      empty_past_all:    "You don't have past appointments.",
      empty_past_flt:    "No past appointments with this status.",

      // Status badges
      status_unconfirmed:"Unconfirmed",
      status_confirmed:  "Confirmed",
      status_in_progress:"In progress",
      status_ready:      "Ready for pickup",
      status_completed:  "Completed",
      status_cancelled:  "Cancelled",

      // WO progress descriptions
      wo_received:       "We received your vehicle",
      wo_diagnosing:     "Reviewing your vehicle",
      wo_awaiting_auth:  "Awaiting your authorization",
      wo_authorized:     "Ready to start repair",
      wo_in_progress:    "Working on your vehicle",
      wo_waiting_parts:  "Waiting for parts",
      wo_ready:          "Ready for pickup!",
      wo_pending_conf:   "Pending confirmation",
      wo_being_attended: "Your vehicle is being serviced",
      wo_appt_confirmed: "Your appointment is confirmed",

      // Card actions
      btn_view_detail:   "View details",
      btn_cancel:        "Cancel",

      // Vehicles page
      page_veh_eyebrow:  "My Cars",
      page_veh_title:    "My Vehicles",
      page_veh_sub:      "All vehicles associated with your account.",
      veh_registered:    "Registered vehicles",
      btn_add_vehicle:   "Add vehicle",
      btn_reload:        "Reload",
      empty_no_vehicles: "You don't have vehicles registered in your account.",
      modal_add_veh_title:"Add vehicle",
      modal_add_veh_sub: "Register a new car in your account",
      ph_plate_veh:      "E.g.: ABC123",
      ph_make_veh:       "E.g.: Toyota",
      ph_model_veh:      "E.g.: Corolla",
      ph_year_veh:       "E.g.: 2020",
      ph_color_veh:      "E.g.: Silver",
      lbl_image_url:     "Image URL (optional)",
      ph_image_url:      "https://...",
      btn_save_vehicle:  "Save vehicle",

      // Appointment detail
      back_to_appts:     "Back to my appointments",
      wo_section_title:  "Your vehicle's status",
      step_received:     "Received",
      step_diagnostic:   "Diagnostic",
      step_repair:       "Repair",
      step_ready:        "Ready",
      wo_detail_title:   "Your work order",
      wo_symptoms:       "Reported symptoms",
      wo_diagnosis_f:    "Workshop diagnosis",
      wo_notes_f:        "Notes",
      wo_services_s:     "Services",
      wo_products_s:     "Products",
      wo_col_desc:       "Description",
      wo_col_qty:        "Qty",
      wo_col_unit:       "Unit",
      wo_col_total:      "Total",
      wo_no_services:    "No services registered.",
      wo_computed_total: "Calculated total",
      wo_no_info:        "No information registered in this order yet.",
      sidebar_workshop:  "Workshop message",
      sidebar_appt_det:  "Appointment details",
      sidebar_appt_date: "Appointment date",
      sidebar_service:   "Service",
      sidebar_req_work:  "Requested work",
      sidebar_notes:     "Notes",
      sidebar_no_wo:     "Your appointment is confirmed",
      sidebar_no_wo_d:   "The workshop will open the work order upon receiving your vehicle.",
      btn_cancel_appt:   "Cancel this appointment",

      // Work orders page
      page_wo_eyebrow:   "History",
      page_wo_title:     "My Work Orders",
      page_wo_sub:       "Review details of all services performed on your vehicle.",
      wo_registered:     "Registered orders",
      btn_expand:        "View details",
      wo_subtotal_svc:   "Subtotal services",
      wo_subtotal_prod:  "Subtotal products",
      wo_opened:         "Opened",
      wo_closed_lbl:     "Closed",
      col_qty:           "Qty",
      col_unit:          "Unit",
      wo_no_products:    "No products registered.",
      empty_no_orders:   "You don't have work orders registered.",

      // WO status labels
      wo_status_open:    "Open",
      wo_status_diag:    "Diagnosing",
      wo_status_prog:    "In progress",
      wo_status_parts:   "Waiting for parts",
      wo_status_auth:    "Pending authorization",
      wo_status_authd:   "Authorized",
      wo_status_ready:   "Ready to deliver",
      wo_status_closed:  "Closed",
      wo_status_done:    "Completed",
      wo_status_cancel:  "Cancelled",

      // Vehicle history
      back_to_vehicles:  "My Vehicles",
      veh_file_label:    "Vehicle file",
      history_title:     "Service history",
      btn_refresh_hist:  "Refresh",
      empty_no_history:  "No services registered for this vehicle yet.",
      svc_singular:      "service",
      svc_plural:        "services",
      prod_singular:     "product",
      prod_plural:       "products",
      wo_diagnosis_lbl:  "Diagnosis",
      wo_no_entries:     "No services or products registered.",

      // Profile modal
      profile_title:     "My profile",
      profile_sub:       "Review and edit your personal information",
      profile_name:      "Full name",
      profile_email:     "Email",
      profile_phone:     "Phone (optional)",
      btn_save_changes:  "Save changes",
    }
  };

  // ─────────────────────────────────────────────────────────────
  // STATE
  // ─────────────────────────────────────────────────────────────
  var _lang = localStorage.getItem("lubri_lang") || "es";

  // ─────────────────────────────────────────────────────────────
  // CORE FUNCTIONS
  // ─────────────────────────────────────────────────────────────
  function t(key) {
    return (T[_lang] || T.es)[key] || key;
  }

  function applyLang(lang) {
    _lang = lang;
    localStorage.setItem("lubri_lang", lang);
    document.documentElement.lang = lang;

    // Update text content
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var val = t(el.getAttribute("data-i18n"));
      if (val) el.textContent = val;
    });

    // Update placeholders
    document.querySelectorAll("[data-i18n-ph]").forEach(function (el) {
      var val = t(el.getAttribute("data-i18n-ph"));
      if (val) el.placeholder = val;
    });

    // Sync toggle button active state
    document.querySelectorAll(".lang-opt[data-lang]").forEach(function (opt) {
      opt.classList.toggle("active", opt.getAttribute("data-lang") === lang);
    });

    // Re-render dynamic content if page registered a refresh function
    if (typeof window.__i18nRefresh === "function") {
      try { window.__i18nRefresh(); } catch (e) {}
    }
  }

  function toggle() {
    applyLang(_lang === "es" ? "en" : "es");
  }

  // ─────────────────────────────────────────────────────────────
  // TOGGLE BUTTON INJECTION
  // ─────────────────────────────────────────────────────────────
  var TOGGLE_BTN = '<button class="lang-toggle" title="Switch language / Cambiar idioma" aria-label="Cambiar idioma"><span class="lang-opt" data-lang="es">ES</span><span class="lang-opt" data-lang="en">EN</span></button>';

  function injectToggle() {
    // Client portal pages: prepend into .nav-user (before notification bell)
    var navUser = document.querySelector(".nav-user");
    if (navUser && !navUser.querySelector(".lang-toggle")) {
      navUser.insertAdjacentHTML("afterbegin", TOGGLE_BTN);
    }

    // Index / auth pages: inject before .nav-login
    var navLogin = document.querySelector(".nav-login");
    if (navLogin && !navLogin.querySelector(".lang-toggle")) {
      navLogin.insertAdjacentHTML("beforebegin", '<div class="lang-toggle-nav d-none d-lg-flex align-items-center ms-auto">' + TOGGLE_BTN + '</div>');
    }

    // Mobile drawer: append a lang row at the end
    var drawer = document.querySelector(".mobile-drawer");
    if (drawer && !drawer.querySelector(".lang-toggle")) {
      drawer.insertAdjacentHTML("beforeend", '<div class="drawer-lang-row">' + TOGGLE_BTN + '</div>');
    }
  }

  // ─────────────────────────────────────────────────────────────
  // INIT
  // ─────────────────────────────────────────────────────────────
  function domInit() {
    injectToggle();
    applyLang(_lang);

    document.addEventListener("click", function (e) {
      if (e.target.closest(".lang-toggle")) {
        toggle();
      }
    });
  }

  // Expose public API immediately (before DOM ready)
  window.i18n = { t: t, applyLang: applyLang, lang: function () { return _lang; } };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", domInit);
  } else {
    domInit();
  }
})();
