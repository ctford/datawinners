from django.utils.translation import ugettext
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.field import IntegerField, TextField, DateField, SelectField, GeoCodeField, TelephoneNumberField, HierarchyField
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME
from mangrove.form_model.validation import NumericRangeConstraint, TextLengthConstraint, RegexConstraint
from mangrove.utils.helpers import slugify
from mangrove.utils.types import is_not_empty, is_empty
from datawinners.entity.helper import question_code_generator

class QuestionnaireBuilder( object ):
    def __init__(self, form_model, dbm, question_builder=None):
        if question_builder is None: question_builder = QuestionBuilder( dbm )
        self.form_model = form_model
        self.question_builder = question_builder
        self.question_code_generator = question_code_generator( )

    def update_questionnaire_with_questions(self, question_set, max_code=1):
        self.form_model.delete_all_fields( )
        language = self.form_model.activeLanguages[0]

        if self.form_model.entity_defaults_to_reporter( ):
            self.form_model.add_field( self.question_builder.create_entity_id_question_for_activity_report( language ) )

        for question in question_set:
            question_code = question['code']
            if question_code == 'code':
                max_code += 1
                question_code = 'q%s' % max_code
            self.form_model.add_field( self.question_builder.create_question( question, language, question_code ) )


class QuestionBuilder( object ):
    def __init__(self, dbm):
        self.dbm = dbm


    def create_question(self, post_dict, language, code):
        ddtype = self._get_ddtype( post_dict )

        if post_dict["type"] == "text":
            return self._create_text_question( post_dict, ddtype, language, code )
        if post_dict["type"] == "integer":
            return self._create_integer_question( post_dict, ddtype, language, code )
        if post_dict["type"] == "geocode":
            return self._create_geo_code_question( post_dict, ddtype, language, code )
        if post_dict["type"] == "select":
            return self._create_select_question( post_dict, False, ddtype, language, code )
        if post_dict["type"] == "date":
            return self._create_date_question( post_dict, ddtype, language, code )
        if post_dict["type"] == "select1":
            return self._create_select_question( post_dict, True, ddtype, language, code )
        if post_dict["type"] == "telephone_number":
            return self._create_telephone_number_question( post_dict, ddtype, language, code )
        if post_dict["type"] == "list":
            return self._create_location_question( post_dict, ddtype, language, code )

    def _get_or_create_data_dict(self, name, slug, primitive_type, description=None):
        try:
            #  Check if is existing
            ddtype = get_datadict_type_by_slug( self.dbm, slug )
        except DataObjectNotFound:
            #  Create new one
            ddtype = create_datadict_type( dbm=self.dbm, name=name, slug=slug,
                                           primitive_type=primitive_type, description=description )
        return ddtype

    def create_entity_id_question_for_activity_report(self, language):
        entity_id_code = "eid"
        entity_data_dict_type = self._get_or_create_data_dict( name=entity_id_code, slug="entity_id",
                                                               primitive_type="string",
                                                               description="Entity ID" )
        name = ugettext( "I am submitting this data on behalf of" )
        entity_id_question = TextField( name=name, code=entity_id_code,
                                        label=name,
                                        entity_question_flag=True, ddtype=entity_data_dict_type,
                                        constraints=[TextLengthConstraint( min=1, max=12 )],
                                        instruction=ugettext( "Choose Data Sender from this list." ),
                                        language=language )
        return entity_id_question


    def _get_name(self, post_dict):
        name = post_dict.get( "name" )
        return name if name is not None else post_dict["title"]

    def _create_text_question(self, post_dict, ddtype, language, code):
        max_length_from_post = post_dict.get( "max_length" )
        min_length_from_post = post_dict.get( "min_length" )
        max_length = max_length_from_post if not is_empty( max_length_from_post ) else None
        min_length = min_length_from_post if not is_empty( min_length_from_post ) else None
        constraints = []
        if not (max_length is None and min_length is None):
            constraints.append( TextLengthConstraint( min=min_length, max=max_length ) )
        return TextField( name=self._get_name( post_dict ), code=code, label=post_dict["title"],
                          entity_question_flag=post_dict.get( "is_entity_question" ), constraints=constraints,
                          ddtype=ddtype,
                          instruction=post_dict.get( "instruction" ), required=post_dict.get( "required" ),
                          language=language )


    def _create_integer_question(self, post_dict, ddtype, language, code):
        max_range_from_post = post_dict.get( "range_max" )
        min_range_from_post = post_dict.get( "range_min" )
        max_range = max_range_from_post if not is_empty( max_range_from_post ) else None
        min_range = min_range_from_post if not is_empty( min_range_from_post ) else None
        range = NumericRangeConstraint( min=min_range, max=max_range )
        return IntegerField( name=self._get_name( post_dict ), code=code, label=post_dict["title"],
                             constraints=[range], ddtype=ddtype, instruction=post_dict.get( "instruction" ),
                             required=post_dict.get( "required" ), language=language )


    def _create_date_question(self, post_dict, ddtype, language, code):
        return DateField( name=self._get_name( post_dict ), code=code, label=post_dict["title"],
                          date_format=post_dict.get( 'date_format' ), ddtype=ddtype,
                          instruction=post_dict.get( "instruction" ),
                          required=post_dict.get( "required" ),
                          event_time_field_flag=post_dict.get( 'event_time_field_flag', False ), language=language )


    def _create_geo_code_question(self, post_dict, ddtype, language, code):
        return GeoCodeField( name=self._get_name( post_dict ), code=code, label=post_dict["title"],
                             ddtype=ddtype,
                             instruction=post_dict.get( "instruction" ), required=post_dict.get( "required" ),
                             language=language )


    def _create_select_question(self, post_dict, single_select_flag, ddtype, language, code):
        options = [(choice.get( "text" ), choice.get( "val" )) for choice in post_dict["choices"]]
        return SelectField( name=self._get_name( post_dict ), code=code, label=post_dict["title"],
                            options=options, single_select_flag=single_select_flag, ddtype=ddtype,
                            instruction=post_dict.get( "instruction" ), required=post_dict.get( "required" ),
                            language=language )


    def _create_telephone_number_question(self, post_dict, ddtype, language, code):
        return TelephoneNumberField( name=self._get_name( post_dict ), code=code,
                                     label=post_dict["title"], ddtype=ddtype,
                                     instruction=post_dict.get( "instruction" ), constraints=(
                self._create_constraints_for_mobile_number( )), required=post_dict.get( "required" ),
                                     language=language )

    def _create_constraints_for_mobile_number(self):
        mobile_number_length = TextLengthConstraint( max=15 )
        mobile_number_pattern = RegexConstraint( reg='^[0-9]+$' )
        mobile_constraints = [mobile_number_length, mobile_number_pattern]
        return mobile_constraints

    def _create_location_question(self, post_dict, ddtype, language, code):
        return HierarchyField( name=LOCATION_TYPE_FIELD_NAME, code=code,
                               label=post_dict["title"], ddtype=ddtype, instruction=post_dict.get( "instruction" ),
                               required=post_dict.get( "required" ), language=language )

    def _get_ddtype(self, post_dict):
        options = post_dict.get( 'options' )
        datadict_type = options.get( 'ddtype' ) if options is not None else None
        if is_not_empty( datadict_type ):
            #  question already has a data dict type
            datadict_slug = datadict_type.get( 'slug' )
        else:
            datadict_slug = str( slugify( unicode( post_dict.get( 'title' ) ) ) )
        ddtype = self._get_or_create_data_dict( name=post_dict.get( 'code' ), slug=datadict_slug,
                                                primitive_type=post_dict.get( 'type' ),
                                                description=post_dict.get( 'title' ) )
        return ddtype


