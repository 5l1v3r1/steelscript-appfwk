from rvbd_portal.apps.datasource.modules.analysis import AnalysisTable
from rvbd_portal.apps.datasource.models import TableField, Column

from rvbd_portal.apps.report.models import Report, Section
from rvbd_portal.apps.report.modules import raw

from rvbd_portal.apps.report.tests.reports import criteria_functions as funcs

report = Report(title='Criteria Parents', hidden_fields = ['report_computed',
                                                           'section_computed',
                                                           'table_computed'] )
report.save()

# Report-level independent
TableField.create(keyword='report_independent', label='Report Independent', obj=report)

# Report-level computed
TableField.create(keyword='report_computed', obj=report,
                  post_process_template='report_computed:{report_independent}',
                  hidden=False)

# Section
section = Section(report=report, title='Section 0')
section.save()

# Section-level computed
TableField.create(keyword='section_computed', obj=section,
                  post_process_template='section_computed:{report_computed}',
                  hidden=False)

# Table
a = AnalysisTable.create('test-criteria-postprocess', tables={},
                         function=funcs.analysis_echo_criteria)

# Table-level computed
TableField.create(keyword='table_computed', obj=a,
                  post_process_template='table_computed:{section_computed}',
                  hidden=False)

a.add_column('key', 'Key', iskey=True, datatype="string")
a.add_column('value', 'Value', datatype="string")

raw.TableWidget.create(section, a, 'Table')
