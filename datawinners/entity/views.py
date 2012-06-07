# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from collections import defaultdict
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import  get_current_site
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.utils import translation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.http import int_to_base36
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _
from mangrove.form_model.field import field_to_json
from mangrove.transport import Channel
from datawinners.alldata.helper import get_visibility_settings_for
from datawinners.accountmanagement.models import NGOUserProfile, get_ngo_admin_user_profiles_for, Organization
from datawinners.accountmanagement.views import is_datasender, is_new_user, _get_email_template_name_for_reset_password,\
    is_not_expired
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.entity.helper import create_registration_form, process_create_datasender_form,\
    delete_datasender_for_trial_mode, delete_entity_instance, delete_datasender_from_project,\
    delete_datasender_users_if_any
from datawinners.entity.import_data import load_all_subjects_of_type, get_entity_type_fields
from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy
from datawinners.main.utils import get_database_manager, include_of_type
from datawinners.messageprovider.message_handler import get_success_msg_for_registration_using, get_submission_error_message_for, get_exception_message_for

from datawinners.messageprovider.messages import exception_messages, WEB
from datawinners.project.models import Project, get_all_projects
from mangrove.datastore.entity_type import  define_type
from mangrove.errors.MangroveException import EntityTypeAlreadyDefined, MangroveException, DataObjectAlreadyExists, QuestionCodeAlreadyExistsException, EntityQuestionAlreadyExistsException, DataObjectNotFound, QuestionAlreadyExistsException
from datawinners.entity.forms import EntityTypeForm, ReporterRegistrationForm
from mangrove.form_model.form_model import REGISTRATION_FORM_CODE, LOCATION_TYPE_FIELD_CODE, REPORTER, get_form_model_by_entity_type, get_form_model_by_code, GEO_CODE_FIELD_NAME, NAME_FIELD
from mangrove.transport.player.player import WebPlayer
from mangrove.transport import Request, TransportInfo
from datawinners.entity import import_data as import_module
from mangrove.utils.types import is_empty
from datawinners.project.web_questionnaire_form_creator import\
    WebQuestionnaireFormCreater
from datawinners.submission.location import LocationBridge
from datawinners.utils import get_excel_sheet, workbook_add_sheet, get_organization, get_organization_country, get_database_manager_for_org
from datawinners.entity.helper import get_country_appended_location, add_imported_data_sender_to_trial_organization
from datawinners.questionnaire.questionnaire_builder import QuestionnaireBuilder
import xlwt
from django.contrib import messages
from datawinners.settings import HNI_SUPPORT_EMAIL_ID, EMAIL_HOST_USER
from mangrove.datastore.entity import get_by_short_code

COUNTRY = ',MADAGASCAR'

#TODO This method has to be moved into a proper place since this is used for registering entities.
@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@login_required(login_url='/login')
@is_not_expired
def submit(request):
    dbm = get_database_manager(request.user)
    post = json.loads(request.POST['data'])
    success = True
    try:
        web_player = WebPlayer(dbm,
            LocationBridge(location_tree=get_location_tree(), get_loc_hierarchy=get_location_hierarchy))
        message = post['message']
        message[LOCATION_TYPE_FIELD_CODE] = get_country_appended_location(message.get(LOCATION_TYPE_FIELD_CODE),
            get_organization_country(request))
        request = Request(message=message,
            transportInfo=TransportInfo(transport=post.get('transport'), source=post.get('source'),
                destination=post.get('destination')))
        response = web_player.accept(request)
        if response.success:
            message = get_success_msg_for_registration_using(response, "web")
        else:
            message = get_submission_error_message_for(response.errors)
        entity_id = response.datarecord_id
    except DataObjectAlreadyExists as exception:
        message = _("Entity with Unique Identification Number (ID) = %s already exists.") % exception.data[1]
        success, entity_id = False, None
    except MangroveException as exception:
        message = get_exception_message_for(exception=exception, channel="web")
        message = _("Please add subject type and then add a subject") if message == "t should be present" else message
        success = False
        entity_id = None
    return HttpResponse(json.dumps({'success': success, 'message': message, 'entity_id': entity_id}))


@login_required(login_url='/login')
@is_not_expired
def create_datasender(request):
    if request.method == 'GET':
        form = ReporterRegistrationForm()
        return render_to_response('entity/create_datasender.html', {'form': form},
            context_instance=RequestContext(request))
    if request.method == 'POST':
        dbm = get_database_manager(request.user)
        form = ReporterRegistrationForm(request.POST)
        org_id = request.user.get_profile().org_id
        reporter_id, message = process_create_datasender_form(dbm, form, org_id)
        if len(form.errors) == 0 and form.requires_web_access():
            email_id = request.POST['email']
            create_single_web_user(org_id=org_id, email_address=email_id, reporter_id=reporter_id,
                language_code=request.LANGUAGE_CODE)

        if message is not None:
            form = ReporterRegistrationForm(initial={'project_id': form.cleaned_data['project_id']})
        return render_to_response('datasender_form.html',
                {'form': form, 'message': message},
            context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_not_expired
def create_type(request):
    success = False
    form = EntityTypeForm(request.POST)
    if form.is_valid():
        entity_name = form.cleaned_data["entity_type_regex"]
        entity_name = [entity_name.strip().lower()]
        try:
            manager = get_database_manager(request.user)
            define_type(manager, entity_name)
            create_registration_form(manager, entity_name)
            message = _("Entity definition successful")
            success = True
        except EntityTypeAlreadyDefined:
            if request.POST["referer"] == 'project':
                message = _("%s already registered as a subject type. Please select %s from the drop down menu.") % (
                    entity_name[0], entity_name[0])
            else:
                message = _("%s already registered as a subject type.") % (entity_name[0],)
    else:
        message = form.fields['entity_type_regex'].error_messages['invalid']
    return HttpResponse(json.dumps({'success': success, 'message': _(message)}))


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_new_user
@is_datasender
@is_not_expired
def all_subjects(request):
    manager = get_database_manager(request.user)
    if request.method == 'POST':
        error_message, failure_imports, success_message, imported_entities = import_module.import_data(request, manager)
        subjects_data = import_module.load_all_subjects(manager)
        return HttpResponse(json.dumps(
                {'success': error_message is None and is_empty(failure_imports), 'message': success_message,
                 'error_message': error_message,
                 'failure_imports': failure_imports, 'all_data': subjects_data, 'imported': imported_entities.keys()}))
    subjects_data = import_module.load_all_subjects(manager)
    return render_to_response('entity/all_subjects.html',
            {'all_data': subjects_data, 'current_language': translation.get_language()},
        context_instance=RequestContext(request))


def get_success_message(entity_type):
    if entity_type == REPORTER:
        return _("Data Sender(s) successfully deleted.")
    return _("Subject(s) successfully deleted.")


def _get_full_name(user):
    return user.first_name + ' ' + user.last_name


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_new_user
@is_datasender
def delete_entity(request):
    manager = get_database_manager(request.user)
    organization = get_organization(request)
    transport_info = TransportInfo("web", request.user.username, "")
    entity_type = request.POST['entity_type']
    all_ids = request.POST['all_ids'].split(';')
    ngo_admin_user_profile = get_ngo_admin_user_profiles_for(organization)[0]
    if ngo_admin_user_profile.reporter_id in all_ids:
        messages.error(request, _("Your organization's account Administrator %s cannot be deleted") %
                                (_get_full_name(ngo_admin_user_profile.user)), "error_message")
    else:
        delete_entity_instance(manager, all_ids, entity_type, transport_info)
        if entity_type == REPORTER:
            delete_datasender_from_project(manager, all_ids)
            delete_datasender_users_if_any(all_ids, organization)
            if organization.in_trial_mode:
                delete_datasender_for_trial_mode(manager, all_ids, entity_type)
        messages.success(request, get_success_message(entity_type))
    return HttpResponse(json.dumps({'success': True}))


def _get_project_association(projects):
    project_association = defaultdict(list)
    for project in projects:
        for datasender in project['value']['data_senders']:
            project_association[datasender].append(project['value']['name'])
    return project_association


def send_reset_password_email(user, language_code):
    reset_form = PasswordResetForm({"email": user.email})
    reset_form.is_valid()
    reset_form.save(email_template_name=_get_email_template_name_for_reset_password(language_code))


def __create_web_users(org_id, reporter_details, language_code, is_create_data_sender=True):
    duplicate_email_ids = User.objects.filter(email__in=[x['email'] for x in reporter_details]).values('email')
    errors = []
    dbm = get_database_manager_for_org(Organization.objects.get(org_id=org_id))
    if len(duplicate_email_ids) > 0:
        for duplicate_email in duplicate_email_ids:
            errors.append("User with email %s already exists" % duplicate_email['email'])
        content = json.dumps({'success': False, 'errors': errors})
    else:
        for reporter in reporter_details:
            reporter_entity = get_by_short_code(dbm, reporter['reporter_id'], [REPORTER])
            user = User.objects.create_user(reporter['email'], reporter['email'], 'test123')
            group = Group.objects.filter(name="Data Senders")[0]
            user.groups.add(group)
            user.first_name = reporter_entity.value(NAME_FIELD)
            user.save()
            profile = NGOUserProfile(user=user, org_id=org_id, title="Mr",
                reporter_id=reporter['reporter_id'])
            profile.save()

            send_reset_password_email(user,
                language_code) if is_create_data_sender else send_activation_email_for_data_sender(user, language_code)

        content = json.dumps({'success': True, 'message': "Users has been created"})
    return content


def create_single_web_user(org_id, email_address, reporter_id, language_code):
    """Create single web user from My Data Senders page"""
    return HttpResponse(
        __create_web_users(org_id, [{'email': email_address, 'reporter_id': reporter_id}], language_code))


def send_activation_email_for_data_sender(user, language_code, request=None):
    site = get_current_site(request)
    ctx_dict = {
        'domain': site.domain,
        'uid': int_to_base36(user.id),
        'user': user,
        'token': default_token_generator.make_token(user),
        'protocol': 'http',
        }
    subject = render_to_string('email/activation_email_subject_for_data_sender_account_' + language_code + '.txt')
    subject = ''.join(subject.splitlines())
    message = render_to_string('email/activation_email_for_data_sender_account_' + language_code + '.html', ctx_dict)
    email = EmailMessage(subject, message, EMAIL_HOST_USER, [user.email], [HNI_SUPPORT_EMAIL_ID])
    email.content_subtype = "html"
    email.send()


@login_required(login_url='/login')
@csrf_view_exempt
@is_not_expired
def create_multiple_web_users(request):
    """Create multiple web users from All Data Senders page"""
    org_id = request.user.get_profile().org_id
    if request.method == 'POST':
        post_data = json.loads(request.POST['post_data'])
        content = __create_web_users(org_id, post_data, request.LANGUAGE_CODE, False)
        return HttpResponse(content)


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_new_user
@is_datasender
@is_not_expired
def all_datasenders(request):
    manager = get_database_manager(request.user)
    projects = get_all_projects(manager)
    fields, old_labels, codes = get_entity_type_fields(manager)
    labels = []
    for label in old_labels:
        if label != "What is the mobile number associated with the subject?":
            labels.append(_(label.replace('subject', 'Data Sender')))
        else:
            labels.append(_("What is the Data Sender's mobile number?"))
    grant_web_access = False
    if request.method == 'GET' and int(request.GET.get('web', '0')):
        grant_web_access = True
    if request.method == 'POST':
        error_message, failure_imports, success_message, imported_datasenders = import_module.import_data(request,
            manager)
        all_data_senders = _get_all_datasenders(manager, projects, request.user)
        mobile_number_index = fields.index('mobile_number')
        add_imported_data_sender_to_trial_organization(request, imported_datasenders,
            all_data_senders=all_data_senders, index=mobile_number_index)

        return HttpResponse(json.dumps(
                {'success': error_message is None and is_empty(failure_imports), 'message': success_message,
                 'error_message': error_message,
                 'failure_imports': failure_imports, 'all_data': all_data_senders,
                 'imported_datasenders': imported_datasenders}))

    all_data_senders = _get_all_datasenders(manager, projects, request.user)
    return render_to_response('entity/all_datasenders.html',
            {'all_data': all_data_senders, 'projects': projects, 'grant_web_access': grant_web_access, "labels": labels,
             'current_language': translation.get_language()},
        context_instance=RequestContext(request))


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_new_user
@is_not_expired
def disassociate_datasenders(request):
    manager = get_database_manager(request.user)
    projects = _get_projects(manager, request)

    for project in projects:
        [project.data_senders.remove(id) for id in request.POST['ids'].split(';') if id in project.data_senders]
        project.save(manager)
    return HttpResponse(reverse(all_datasenders))


def _get_projects(manager, request):
    project_ids = request.POST.get('project_id').split(';')
    projects = []
    for project_id in project_ids:
        project = Project.load(manager.database, project_id)
        if project is not None:
            projects.append(project)
    return projects


@csrf_view_exempt
@csrf_response_exempt
@login_required(login_url='/login')
@is_new_user
@is_not_expired
def associate_datasenders(request):
    manager = get_database_manager(request.user)
    projects = _get_projects(manager, request)
    for project in projects:
        project.data_senders.extend([id for id in request.POST['ids'].split(';') if not id in project.data_senders])
        project.save(manager)
    return HttpResponse(reverse(all_datasenders))


def _associate_data_senders_to_project(imported_entities, manager, project_id):
    project = Project.load(manager.database, project_id)
    project.data_senders.extend([k for k, v in imported_entities.items() if v == REPORTER])
    project.save(manager)


@csrf_view_exempt
@csrf_response_exempt
@require_http_methods(['POST'])
@login_required(login_url='/login')
@is_not_expired
def import_subjects_from_project_wizard(request):
    manager = get_database_manager(request.user)
    project_id = request.GET.get('project_id')
    error_message, failure_imports, success_message, imported_entities = import_module.import_data(request, manager)
    if project_id is not None:
        _associate_data_senders_to_project(imported_entities, manager, project_id)
    return HttpResponse(json.dumps(
            {'success': error_message is None and is_empty(failure_imports), 'message': success_message,
             'error_message': error_message,
             'failure_imports': failure_imports}))

def _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class):
    return {'questionnaire_form': questionnaire_form,
            'entity_type': entity_type,
            "disable_link_class": disable_link_class,
            "hide_link_class": hide_link_class,
            'back_to_project_link': reverse("alldata_index"),
            'smart_phone_instruction_link': reverse("smart_phone_instruction"),
            }

def get_template(user):
    return 'entity/register_subject.html' if user.get_profile().reporter else 'entity/web_questionnaire.html'

@login_required(login_url='/login')
@is_not_expired
def create_subject(request, entity_type=None):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_entity_type(manager, [entity_type.lower()])
    QuestionnaireForm = WebQuestionnaireFormCreater(None, form_model=form_model).create()

    web_questionnaire_template = get_template(request.user)
    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)


    if request.method == 'GET':
        questionnaire_form = QuestionnaireForm()
        form_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class)
        return render_to_response(web_questionnaire_template,
                                  form_context,
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        questionnaire_form = QuestionnaireForm(country=get_organization_country(request), data=request.POST)
        if not questionnaire_form.is_valid():
            form_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class)
            return render_to_response(web_questionnaire_template,
                                      form_context,
                                      context_instance=RequestContext(request))

        success_message = None
        error_message = None
        try:
            from datawinners.project.helper import create_request

            response = WebPlayer(manager,
                LocationBridge(location_tree=get_location_tree(), get_loc_hierarchy=get_location_hierarchy)).accept(
                create_request(questionnaire_form, request.user.username))
            if response.success:
                ReportRouter().route(get_organization(request).org_id, response)
                success_message = (_("Successfully submitted. Unique identification number(ID) is:") + " %s") % (
                    response.short_code,)
                questionnaire_form = QuestionnaireForm()
            else:
                from datawinners.project.helper import errors_to_list

                questionnaire_form._errors = errors_to_list(response.errors, form_model.fields)
                form_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class)
                return render_to_response(web_questionnaire_template,
                                          form_context,
                                          context_instance=RequestContext(request))

        except DataObjectNotFound:
            message = exception_messages.get(DataObjectNotFound).get(WEB)
            error_message = _(message) % (form_model.entity_type[0], form_model.entity_type[0])
        except DataObjectAlreadyExists as exception:
            error_message = _("Entity with Unique Identification Number (ID) = %s already exists.") % exception.data[1]
        except Exception as exception:
            error_message = _(get_exception_message_for(exception=exception, channel=Channel.WEB))

        subject_context = _make_form_context(questionnaire_form, entity_type, disable_link_class, hide_link_class)
        subject_context.update({'success_message': success_message, 'error_message': error_message})

        return render_to_response(web_questionnaire_template, subject_context,
            context_instance=RequestContext(request))


def _get_all_datasenders(manager, projects, user):
    all_data_senders, fields, labels = import_module.load_all_subjects_of_type(manager)
    project_association = _get_project_association(projects)
    for datasender in all_data_senders:
        if datasender["short_code"] == "test":
            index = all_data_senders.index(datasender)
            del all_data_senders[index]
            continue
        org_id = NGOUserProfile.objects.get(user=user).org_id
        user_profile = NGOUserProfile.objects.filter(reporter_id=datasender['short_code'], org_id=org_id)
        datasender['email'] = user_profile[0].user.email if len(user_profile) > 0 else "--"
        association = project_association.get(datasender['short_code'])
        datasender['projects'] = ' ,'.join(association) if association is not None else '--'
    return all_data_senders


@login_required(login_url='/login')
@is_not_expired
def edit_subject_questionnaire(request, entity_type=None):
    manager = get_database_manager(request.user)
    if entity_type is None:
        return HttpResponseRedirect(reverse(all_subjects))

    form_model = get_form_model_by_entity_type(manager, [entity_type.lower()])
    if form_model is None:
        form_model = get_form_model_by_code(manager, REGISTRATION_FORM_CODE)
    fields = form_model.fields

    existing_questions = json.dumps(fields, default=field_to_json)
    return render_to_response('entity/questionnaire.html',
            {'existing_questions': repr(existing_questions),
             'questionnaire_code': form_model.form_code,
             'langauge': form_model.activeLanguages[0],
             'entity_type': entity_type,
             'post_url': reverse(save_questionnaire)},
        context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_not_expired
def save_questionnaire(request):
    manager = get_database_manager(request.user)
    if request.method == 'POST':
        new_short_code = request.POST['questionnaire-code'].lower()
        saved_short_code = request.POST['saved-questionnaire-code'].lower()

        form_model = get_form_model_by_code(manager, saved_short_code)
        if new_short_code != saved_short_code:
            try:
                form_model.form_code = new_short_code
                form_model.save()
            except DataObjectAlreadyExists as e:
                if e.message.find("Form") >= 0:
                    return HttpResponse(json.dumps({'success': False,
                                                    'error_message': "Questionnaire with this code already exists"}))
                return HttpResponseServerError(e.message)

        json_string = request.POST['question-set']
        question_set = json.loads(json_string)
        try:
            QuestionnaireBuilder(form_model, manager).update_questionnaire_with_questions(question_set)
            form_model.save()
            return HttpResponse(json.dumps({'success': True, 'form_code': form_model.form_code}))
        except QuestionCodeAlreadyExistsException as e:
            return HttpResponseServerError(e)
        except QuestionAlreadyExistsException as e:
            return HttpResponseServerError(e)
        except EntityQuestionAlreadyExistsException as e:
            return HttpResponseServerError(e.message)


@login_required(login_url='/login')
@is_not_expired
def export_subject(request):
    entity_type = request.POST["entity_type"]
    entity_list = request.POST.getlist("checked")
    manager = get_database_manager(request.user)
    all_data, fields, labels = load_all_subjects_of_type(manager, filter_entities=include_of_type, type=entity_type)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (entity_type,)
    fields, labels, codes = import_module.get_entity_type_fields(manager, entity_type)

    raw_data = [labels]
    for data in all_data:
        if data['short_code'] in entity_list or len(entity_list) == 0:
            raw_data.append(data['cols'])
    wb = get_excel_sheet(raw_data, entity_type)
    codes.insert(0, "form_code")
    ws = workbook_add_sheet(wb, [codes], "codes")
    ws.visibility = 1
    wb.save(response)
    return response


@login_required(login_url='/login')
@is_not_expired
def export_template(request, entity_type=None):
    manager = get_database_manager(request.user)
    if entity_type is None:
        return HttpResponseRedirect(reverse(all_subjects))

    fields, labels, codes = import_module.get_entity_type_fields(manager, entity_type)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (entity_type,)

    wb = get_excel_sheet([labels], entity_type)
    codes.insert(0, "form_code")
    ws = workbook_add_sheet(wb, [codes], "codes")
    ws.visibility = 1
    try:
        index_geocode = fields.index(GEO_CODE_FIELD_NAME)
    except ValueError:
        index_geocode = 0

    ws = wb.get_sheet(0)

    style = xlwt.XFStyle()
    style.num_format_str = '@'
    gps_col = ws.col(index_geocode)
    gps_col.set_style(style)

    wb.save(response)
    return response
