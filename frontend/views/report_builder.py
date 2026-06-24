import streamlit as st


def show_view() -> None:
    """Maritime safety report from pipeline or demo fallback."""
    st.title("Maritime Safety Report")

    report = st.session_state.get("report")
    if report is None:
        st.info("No report yet. Use **Sync Satellite Data** in the sidebar.")
        return

    risk = report.get("risk_level", "N/A")
    st.metric("Risk level", str(risk).upper())

    narrative = report.get("narrative_summary") or report.get("summary")
    if narrative:
        st.subheader("Summary")
        st.write(narrative)

    actions = report.get("recommended_actions", [])
    if actions:
        st.subheader("Recommended actions")
        for action in actions:
            st.markdown(f"- {action}")

    limits = report.get("assumptions_and_limitations", [])
    if limits:
        with st.expander("Assumptions & limitations"):
            for item in limits:
                st.markdown(f"- {item}")
