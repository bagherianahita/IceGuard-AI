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