import streamlit as st


def show_view() -> None:
    """Display the maritime safety report view."""
    st.title("Maritime Safety Report")

    report = st.session_state.get("report")
    if report is None:
        st.info("No safety report has been generated yet. Use 'Sync Satellite Data' to run the analysis.")
        return

    st.subheader("Risk Level")
    risk_level = report.get("risk_level", "N/A")
    st.write(f"**Risk Level**: {risk_level}")

    narrative = report.get("summary") or report.get("narrative_summary")
    if narrative:
        st.subheader("Summary")
        st.write(narrative)

    actions = report.get("recommended_actions", [])
    if actions:
        st.subheader("Recommended Actions")
        for action in actions:
            st.markdown(f"- {action}")

import streamlit as st

def show_view():
    st.title("📝 Maritime Safety Report")
    
    if st.session_state.report:
        report = st.session_state.report
        
        st.error(f"⚠️ RISK LEVEL: {report['risk_level'].upper()}")
        
        with st.expander("See Narrative Summary", expanded=True):
            st.write(report['summary'])
            
        st.subheader("Recommended Actions")
        for action in report['recommended_actions']:
            st.success(f"✅ {action}")
            
        # Download button for professional feel
        st.download_button("Download PDF Report", "Sample Content", "report.pdf")
    else:
        st.info("No report generated yet. Run the analysis to see AI insights.")