from flask import Blueprint, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from export_utils import exporter
from datetime import datetime
import io

exports_bp = Blueprint('exports', __name__, url_prefix='/exports')

@exports_bp.route('/tickets')
@login_required
def export_tickets():
    """Export tickets to Excel"""
    try:
        # Get filters from query parameters
        filters = {}
        
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        
        # Generate Excel file
        excel_file = exporter.create_simple_export("tickets", filters)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tickets_export_{timestamp}.xlsx"
        
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error exporting tickets: {str(e)}', 'error')
        return redirect(request.referrer or url_for('analytics.dashboard'))

@exports_bp.route('/comprehensive-report')
@login_required
def export_comprehensive_report():
    """Export comprehensive analytics report to Excel"""
    try:
        # Get filters from query parameters
        filters = {}
        
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        
        # Generate comprehensive Excel report
        excel_file = exporter.create_comprehensive_report(filters)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tech_support_report_{timestamp}.xlsx"
        
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error exporting report: {str(e)}', 'error')
        return redirect(request.referrer or url_for('analytics.dashboard'))

@exports_bp.route('/api/preview')
@login_required
def preview_export():
    """Preview export data before downloading"""
    try:
        export_type = request.args.get('type', 'tickets')
        
        # Get filters
        filters = {}
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        
        if export_type == 'tickets':
            # Get tickets data for preview
            df = exporter.get_tickets_data(
                start_date=filters.get('start_date'),
                end_date=filters.get('end_date'),
                status=filters.get('status'),
                category=filters.get('category')
            )
            
            # Convert to dict for JSON response
            preview_data = {
                'total_records': len(df),
                'columns': df.columns.tolist(),
                'sample_data': df.head(5).to_dict('records') if len(df) > 0 else [],
                'filters_applied': filters
            }
            
        elif export_type == 'analytics':
            # Get analytics summary for preview
            analytics_data = exporter.get_analytics_summary()
            
            preview_data = {
                'total_tickets': int(analytics_data['overall_stats']['total_tickets'].iloc[0]),
                'categories': len(analytics_data['category_breakdown']),
                'priorities': len(analytics_data['priority_breakdown']),
                'trend_days': len(analytics_data['daily_trend']),
                'filters_applied': filters
            }
        
        return jsonify({
            'success': True,
            'preview': preview_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exports_bp.route('/api/formats')
@login_required
def available_formats():
    """Get available export formats"""
    return jsonify({
        'formats': [
            {
                'id': 'excel_simple',
                'name': 'Excel (Simple)',
                'description': 'Basic Excel export with filtered data',
                'extension': '.xlsx'
            },
            {
                'id': 'excel_comprehensive',
                'name': 'Excel (Comprehensive Report)',
                'description': 'Multi-sheet Excel report with analytics and charts',
                'extension': '.xlsx'
            }
        ]
    })

@exports_bp.route('/custom')
@login_required
def custom_export():
    """Custom export with user-defined parameters"""
    try:
        # Get custom parameters
        data = request.get_json() if request.is_json else request.form
        
        export_format = data.get('format', 'excel_simple')
        include_fields = data.getlist('fields') if hasattr(data, 'getlist') else data.get('fields', [])
        
        filters = {}
        for key in ['start_date', 'end_date', 'status', 'category']:
            if data.get(key):
                filters[key] = data.get(key)
        
        if export_format == 'excel_comprehensive':
            excel_file = exporter.create_comprehensive_report(filters)
            filename_prefix = "comprehensive_report"
        else:
            excel_file = exporter.create_simple_export("tickets", filters)
            filename_prefix = "tickets_export"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
