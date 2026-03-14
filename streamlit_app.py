import streamlit as st
import os
import sys
import tempfile

st.set_page_config(
    page_title="LangFlow 工作流对话系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 LangFlow 工作流对话系统")
st.markdown("---")

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'workflow_code' not in st.session_state:
    st.session_state.workflow_code = ''

if 'workflow_loaded' not in st.session_state:
    st.session_state.workflow_loaded = False

if 'current_state' not in st.session_state:
    st.session_state.current_state = None

if 'graph_builder' not in st.session_state:
    st.session_state.graph_builder = None

with st.sidebar:
    st.header("📦 加载工作流")
    
    st.markdown("### 方式 1: 粘贴代码")
    code_input = st.text_area(
        "粘贴生成的 Python 代码",
        height=300,
        value=st.session_state.workflow_code
    )
    
    if st.button("📥 加载代码", type="primary", use_container_width=True):
        if code_input.strip():
            st.session_state.workflow_code = code_input
            st.session_state.workflow_loaded = True
            st.session_state.messages = []
            st.session_state.current_state = None
            st.session_state.graph_builder = None
            st.success("工作流代码加载成功！")
            st.rerun()
        else:
            st.error("请先输入工作流代码")
    
    st.markdown("---")
    
    st.markdown("### 方式 2: 上传文件")
    uploaded_file = st.file_uploader("选择生成的 .py 文件", type=["py"])
    if uploaded_file is not None:
        code_content = uploaded_file.read().decode('utf-8')
        st.session_state.workflow_code = code_content
        st.session_state.workflow_loaded = True
        st.session_state.messages = []
        st.session_state.current_state = None
        st.session_state.graph_builder = None
        st.success(f"文件 {uploaded_file.name} 加载成功！")
        st.rerun()
    
    st.markdown("---")
    
    if st.session_state.workflow_loaded:
        if st.button("🔄 重置对话", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_state = None
            st.rerun()
        
        if st.button("🗑️ 卸载工作流", type="secondary", use_container_width=True):
            st.session_state.workflow_code = ''
            st.session_state.workflow_loaded = False
            st.session_state.messages = []
            st.session_state.current_state = None
            st.session_state.graph_builder = None
            st.rerun()

if not st.session_state.workflow_loaded:
    st.info("👈 请先从左侧侧边栏加载工作流代码")
    
    st.markdown("""
    ## 如何使用
    
    1. 在 LangFlow 编辑器中设计你的工作流
    2. 生成 Python 代码
    3. 将代码粘贴或上传到这里
    4. 开始与你的工作流对话！
    
    ## 示例工作流
    
    你可以创建面试系统、客服助手、知识问答等各种应用！
    """)
else:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 对话界面")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("输入你的消息..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    with st.spinner("工作流运行中..."):
                        temp_dir = tempfile.mkdtemp()
                        workflow_path = os.path.join(temp_dir, "workflow.py")
                        
                        with open(workflow_path, 'w', encoding='utf-8') as f:
                            f.write(st.session_state.workflow_code)
                        
                        sys.path.insert(0, temp_dir)
                        
                        exec_globals = {}
                        exec(st.session_state.workflow_code, exec_globals)
                        
                        if 'build_graph' not in exec_globals:
                            full_response = "错误：工作流代码中未找到 build_graph 函数"
                            message_placeholder.error(full_response)
                        else:
                            if st.session_state.graph_builder is None:
                                st.session_state.graph_builder = exec_globals['build_graph']
                            
                            app = st.session_state.graph_builder()
                            
                            if st.session_state.current_state is None:
                                st.session_state.current_state = {
                                    'messages': [],
                                    'query': prompt,
                                    'output': ''
                                }
                            else:
                                st.session_state.current_state['query'] = prompt
                            
                            result = app.invoke(st.session_state.current_state)
                            
                            st.session_state.current_state = result
                            
                            output_var = 'output'
                            if 'OUTPUT_VARIABLE' in exec_globals:
                                output_var = exec_globals['OUTPUT_VARIABLE']
                            
                            response = result.get(output_var, '')
                            if not response:
                                response = str(result)
                            
                            full_response = response
                            message_placeholder.markdown(full_response)
                
                except Exception as e:
                    full_response = f"运行出错: {str(e)}"
                    message_placeholder.error(full_response)
                    st.exception(e)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    with col2:
        st.header("⚙️ 工作流信息")
        
        with st.expander("📝 查看工作流代码", expanded=False):
            st.code(st.session_state.workflow_code, language='python')
        
        st.markdown("---")
        
        st.header("📊 对话历史")
        st.write(f"消息数: {len(st.session_state.messages)}")
        
        if st.session_state.messages:
            st.markdown("---")
            for i, msg in enumerate(reversed(st.session_state.messages[-10:])):
                role = "👤" if msg["role"] == "user" else "🤖"
                st.markdown(f"**{role} {msg['role']}**: {msg['content'][:50]}...")
        
        if st.session_state.current_state:
            st.markdown("---")
            st.header("🔍 当前状态")
            with st.expander("查看完整状态", expanded=False):
                st.json(st.session_state.current_state)

st.markdown("---")
st.caption("LangFlow 工作流对话系统 - 基于 Streamlit")
