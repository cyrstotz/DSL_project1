# === to-latex-folder.py (with last_known_task tracking per student) ===
from pathlib import Path
import base64
import time
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import re
from collections import defaultdict

EXAM_QUESTIONS_NL = """
    Task 1: Reactor (15 points)

    Problem Setup:
    A reactor operates in steady state with an inlet mass flow rate of \( \dot{m}_{in} = 0.3 \, \text{kg/s} \), and the temperature at the inlet is \( T_{in} = 70^\circ \text{C} \), which is assumed to be boiling liquid (saturated liquid). At the outlet, the flow exits at \( T_{out} = 100^\circ \text{C} \) as a saturated liquid. The mass of the reaction mixture in the reactor remains constant, \( m_{\text{total},1} = 5755 \, \text{kg} \), and the steam quality is \( x_D = \frac{m_D}{m_{\text{total}}} = 0.005 \) with a reactor temperature of \( T_{\text{Reactor},1} = 100^\circ \text{C} \). In the reactor, a chemical reaction occurs, releasing a heat flow \( \dot{Q}_R = 100 \, \text{kW} \). To prevent the reactor's temperature from rising, the heat flow is removed through the cooling jacket. The coolant enters at a temperature of \( T_{KF,in} = 288.15 \, \text{K} \) and exits at \( T_{KF,out} = 298.15 \, \text{K} \).

    Assumptions:
    - Kinetic and potential energies are negligible.
    - The reaction mixture is assumed to be pure water.
    - Use water tables (A-2 to A-6) to determine substance properties.
    - The coolant in the jacket is modeled as an ideal liquid with constant heat capacity.
    - The reaction heat is modeled as an incoming heat flow.
    - Heat transfer occurs only through the cooling jacket.
    - The cooling jacket and reactor are adiabatic to the surroundings.
    - The pressure remains constant in the cooling jacket.

    Image Description: 
    Figure 1 shows the reactor in steady-state operation with a cooling jacket. The diagram includes the inlet and outlet flows of the liquid, temperature values for both the reactor's contents and the coolant, as well as the heat transfer through the reactor's wall to the cooling fluid.

    Subtasks:
    a) Determine the heat flow \( \dot{Q}_{out} \) transferred from the reactor wall to the coolant.

    b) Determine the thermodynamic mean temperature \( T_{KF} \) of the coolant stream.

    c) Determine the entropy production \( \dot{S}_{erz} \) resulting from the heat transfer between the reactor and the cooling jacket.

    After the steady-state operation is stopped, the reactor's temperature is to be cooled from \( T_{\text{Reactor},1} = 100^\circ \text{C} \) to \( T_{\text{Reactor},2} = 70^\circ \text{C} \). A mass \( \Delta m_{12} \) of water, as boiling liquid at \( T_{in,12} = 20^\circ \text{C} \), is added. The released reaction heat between states 1 and 2 corresponds to the heat removed via the cooling jacket (\( Q_{R,12} = Q_{out,12} = 35 \, \text{MJ} \)). Assume that at state 2, the entire mass in the reactor is in the form of boiling liquid.

    d) Determine the mass of water \Delta m_{12} that needs to be added in order to cool the reactor’s temperature T_{\text{Reactor},2} = 70^\circ \text{C} using an energy balance.

    e) Determine the entropy change \( \Delta S_{12} \) of the reactor contents between states 1 and 2.

    ---

    Task 2: Exergy in a Jet Engine (19 points)

    Problem Setup:
    A jet engine operates at an airspeed of \( w_{\text{Luft}} = 200 \, \text{m/s} \) with surrounding conditions \( p_0 = 0.191 \, \text{bar} \) and \( T_0 = -30^\circ \text{C} \). The air entering the engine is compressed in an adiabatic pre-compressor with an isentropic efficiency \( \eta_{V,s} < 1 \). The air is then divided into a mantle flow \( \dot{m}_M \) and a core flow \( \dot{m}_K \) with the ratio \( \frac{\dot{m}_M}{\dot{m}_K} = 5.293 \). The core flow undergoes a gas turbine process, which absorbs heat \( q_B = \frac{\dot{Q}_B}{\dot{m}_K} = 1195 \, \text{kJ/kg} \) at a thermodynamic mean temperature \( T_B = 1289 \, \text{K} \). The gas turbine process consists of:
    - Adiabatic, reversible high-pressure compressor
    - Isobaric heat addition in a combustion chamber
    - Adiabatic, irreversible turbine

    After the isobaric mixing chamber (state 5), the temperature is \( T_5 = 431.9 \, \text{K} \), pressure \( p_5 = 0.5 \, \text{bar} \), and velocity \( w_5 = 220 \, \text{m/s} \). The air exits the reversible and adiabatic nozzle (state 6) with atmospheric pressure.

    Assumptions:
    - The air is treated as an ideal gas with a constant specific heat \( c_{p,\text{Luft}} = 1.006 \, \text{kJ/kgK} \) and a constant polytropic exponent \( n = \kappa = 1.4 \).
    - Potential energies can be neglected.
    - The jet engine operates in a steady-state and adiabatic manner.
    - The entire power gained in the turbine is used for driving the pre-compressor and the high-pressure compressor.

    Image Description:
    Figure 2 shows the schematic of the jet engine. It includes components like the pre-compressor, turbine, and exhaust flow. The diagram provides a visual representation of the engine operation.

    Subtasks:
    a) Draw the process qualitatively in a T-s diagram and clearly label the relevant isobars. Provide units on the axes.

    b) Determine the velocity \( w_6 \) and temperature \( T_6 \) at the exit of the jet engine.

    c) Calculate the mass-specific increase in flow exergy \( \Delta ex_{\text{str}} = ex_{\text{str},6} - ex_{\text{str},0} \) between states 0 and 6.

    d) Calculate the mass-specific exergy loss \( ex_{\text{verl}} \) of the jet engine.

    ---

    Task 3: Melting Ice with a Perfect Gas (17 points)

    Problem Setup:
    An isolated cylinder consists of two separated chambers. The lower chamber contains a perfect gas. The upper chamber contains a solid-liquid equilibrium mixture of water, called "ice-water mixture" (EW). Between the gas and the EW, there is a massless, heat-conducting membrane. On top of the EW, there is an insulating piston with mass \( m_K = 32 \, \text{kg} \), which exerts force on the mixture against atmospheric pressure (\( p_{\text{amb}} = 1 \, \text{bar} \)). The cylinder has a diameter of \( D = 10 \, \text{cm} \).

    At state 1, the gas has a temperature of \( T_{g,1} = 500^\circ \text{C} \) and a volume of \( V_{g,1} = 3.14 \, \text{L} \). The EW has a total mass of \( m_{\text{EW}} = 0.1 \, \text{kg} \), a temperature of \( T_{\text{EW},1} = 0^\circ \text{C} \), and an ice content of \( x_{\text{Ice},1} = \frac{m_{\text{Ice}}}{m_{\text{EW}}} = 0.6 \). The heat flow from the gas causes some of the ice to melt, and the ice content changes to \( x_{\text{Ice},2} \). In this task, the final state of the system (state 2) is to be determined, where no more heat is transferred between the gas and the EW.

    Image Description:
    Figure 4 shows the isolated cylinder with two chambers: one containing the gas and the other the ice-water mixture. A massless membrane separates the two phases.

    Assumptions:
        -	The gas in the cylinder is a perfect gas with an isochoric heat capacity c_V = 0.633 \, \text{kJ/kg·K} and a molar mass M_g = 50 \, \text{kg/kmol}.
        -	Solid and liquid water are incompressible, and the density difference between the phases is negligible. That is, the volume of the ice-water mixture (EW) does not change during melting.
        -	Kinetic and potential energies can be neglected.
        -	In state 2, the gas and the EW are in thermodynamic equilibrium.
        -	The membrane and piston are frictionless in the cylinder.

    Subtasks:
    a) Calculate the pressure of the gas \( p_{g,1} \) in state 1 and the mass of gas \( m_g \) in the cylinder.

    b) In state 2, \( x_{\text{Ice},2} > 0 \). What are the temperature \( T_{g,2} \) and pressure \( p_{g,2} \) of the gas in state 2? Justify your answer in one sentence.

    c) Calculate the heat transfer \( Q_{12} \) that is transferred from the gas to the ice-water mixture between states 1 and 2.

    d) Calculate the final ice content \( x_{\text{Ice},2} \) in state 2. Use Table 1 to determine the states of the EW. The table can be used similarly to a steam table. Provide your answer with three significant digits.

    ---

    Task 4: Freeze Drying with an R134a Cooling Cycle (18.5 points)

    Problem Setup:
    The freeze-drying process is a method used to preserve food by removing moisture. In this example, the process occurs in two steps:

    Step 1:
    The food is frozen inside the freeze dryer using a cooling cycle fed with R134a refrigerant. The food is placed in the freeze dryer, which has already been cooled to temperature \( T_i \). As the food cools and freezes, heat \( \dot{Q}_K \) is removed from the interior through a heat exchanger, where the R134a refrigerant undergoes a complete and isobaric evaporation. The temperature in the evaporator is 6K below the constant interior temperature of the freeze dryer \( T_i \). A compressor then compresses the saturated refrigerant vapor (state 2) adiabatically and reversibly to \( p_3 = 8 \, \text{bar} \) (state 3). The compressed refrigerant is then fully condensed isobarically in a second heat exchanger (state 4) and then expanded adiabatically to the exit pressure (state 1).

    Step 2:
    The pressure inside the freeze dryer is reduced isothermally 5 mbar below the triple point of water to transfer the frozen water in the food to the gas phase through sublimation. The temperature inside the freeze dryer \( T_i \) is 10K above the sublimation point.



    Image Description:
    Figure 5 shows the freeze-drying process and its components, including the compressor, expansion valve, and the various stages of refrigeration and sublimation.

    Assumptions:
        -	The calculation of the cooling cycle (Step i) includes subtasks 4b) to 4d). Tasks 4a) and 4e) can be solved independently from each other.
        -	Use the p-T diagram from Figure 6 to determine the temperature T_i.
        -	Use Tables A-10, A-11, and A-12 to determine the substance properties of Refrigerant 134a.
        -	The temperature T_i inside the freeze dryer (excluding the food) can be assumed to be homogeneous and constant throughout the entire freeze-drying process.
        -	All processes in the cooling cycle during freezing (Step i) can be assumed to be stationary.
        -	The interior of the freeze dryer, the compressor, and the expansion valve are adiabatic to the outside.
        -	Kinetic and potential energies can be neglected.

    Subtasks:
    a) Draw the described freeze-drying process for the water in the food (steps i and ii), including the labeled phase regions in a p-T diagram. Do not use Figure 6, instead create your own diagram.

    b) Determine the required mass flow rate \( \dot{m}_{R134a} \) of the refrigerant in the cooling cycle.

    c) Determine the vapor quality \( x_1 \) of the refrigerant in state 1 right after the expansion valve.

    d) Calculate the coefficient of performance (COP) of the cooling cycle.

    e) How would the temperature inside the freeze dryer evolve in Step ii if the cooling cycle in Step i continued unchanged and a constant heat flow \( \dot{Q}_K \) continued to be removed? Justify your answer.
    """
EXAM_QUESTIONS_Latex = r"""
    Task 1: Reactor (15 points)

    Problem Setup:
    A reactor operates in steady-state with an inlet mass flow rate of \( \dot{m}_{\text{in}} = 0.3 \, \text{kg/s} \) and an inlet temperature of \( T_{\text{in}} = 70^\circ\text{C} \), considered to be saturated liquid. The outlet flow leaves the reactor at \( T_{\text{out}} = 100^\circ\text{C} \), also as saturated liquid. The reactor mass remains constant at \( m_{\text{total},1} = 5755 \, \text{kg} \), with steam quality \( x_D = \frac{m_D}{m_{\text{total}}} = 0.005 \) and reactor temperature \( T_{\text{Reactor},1} = 100^\circ\text{C} \). A chemical reaction releases a heat flow of \( \dot{Q}_R = 100 \, \text{kW} \), which must be removed through a cooling jacket. The coolant enters at \( T_{\text{KF,in}} = 288.15 \, \text{K} \) and exits at \( T_{\text{KF,out}} = 298.15 \, \text{K} \).

    Assumptions:
    - Kinetic and potential energy are negligible.
    - The reaction mixture is considered pure water. Use water tables A-2 to A-6.
    - The coolant is modeled as an ideal liquid with constant heat capacity.
    - The reaction heat is modeled as incoming heat flow.
    - Heat is transferred only to the cooling jacket; the system is adiabatic to the surroundings.
    - Pressure in the cooling jacket remains constant.

    Figure Description:
    Figure 1 shows a steady-state reactor with labeled inlet/outlet streams, temperatures, and heat flows through the reactor wall to the coolant.

    Subtasks:
    a) Determine the heat flow \( \dot{Q}_{\text{out}} \) removed by the coolant.

    b) Determine the thermodynamic mean temperature \( T_{\text{KF}} \) of the coolant.

    c) Determine the entropy production \( \dot{S}_{\text{gen}} \) from the heat transfer between the reactor and the cooling jacket.

    d) After stopping steady-state operation, the temperature is to be reduced from \( 100^\circ\text{C} \) to \( 70^\circ\text{C} \). A mass \( \Delta m_{12} \) of saturated liquid water at \( T_{\text{in,12}} = 20^\circ\text{C} \) is added. The heat released during cooling from state 1 to 2 is \( Q_{R,12} = Q_{\text{out},12} = 35 \, \text{MJ} \). Assume the reactor contents are saturated liquid at state 2. Determine \( \Delta m_{12} \) using an energy balance.

    e) Determine the entropy change \( \Delta S_{12} \) of the reactor contents from state 1 to 2.

    ---
    Task 2: Jet Engine Exergy (19 points)

    Problem Setup:
    A jet engine operates at airspeed \( w_{\text{air}} = 200 \, \text{m/s} \), under ambient conditions \( p_0 = 0.191 \, \text{bar} \), \( T_0 = -30^\circ\text{C} \). Air entering the engine is compressed adiabatically with isentropic efficiency \( \eta_{\text{comp}} < 1 \), then split into a bypass stream \( \dot{m}_M \) and a core stream \( \dot{m}_K \) with \( \frac{\dot{m}_M}{\dot{m}_K} = 5.293 \). The core flow receives heat \( q_B = \frac{\dot{Q}_B}{\dot{m}_K} = 1195 \, \text{kJ/kg} \) at \( \bar{T}_B = 1289 \, \text{K} \). The gas turbine process includes:
    - Reversible, adiabatic high-pressure compressor
    - Isobaric combustion
    - Irreversible, adiabatic turbine

    After the mixing chamber (state 5): \( T_5 = 431.9 \, \text{K} \), \( p_5 = 0.5 \, \text{bar} \), \( w_5 = 220 \, \text{m/s} \). The nozzle exit (state 6) is at \( p_6 = p_0 \).

    Assumptions:
    - Air is an ideal gas with \( c_{p,\text{air}} = 1.006 \, \text{kJ/kg·K} \), \( \kappa = 1.4 \).
    - Potential energy is negligible.
    - The engine operates adiabatically and in steady state.
    - All turbine power is used for compressors.

    Figure Description:
    Figure 2 shows the engine layout: pre-compressor, bypass/core streams, combustion chamber, turbine, mixer, and nozzle with relevant states labeled.

    Subtasks:
    a) Draw the process qualitatively in a T-s diagram with labeled isobars and units on the axes.

    b) Determine the outlet velocity \( w_6 \) and temperature \( T_6 \).

    c) Calculate the mass-specific increase in flow exergy:
    \[
    \Delta ex_{\text{flow}} = ex_{\text{flow},6} - ex_{\text{flow},0}
    \]

    d) Compute the mass-specific exergy destruction \( ex_{\text{dest}} \) in the engine.

    ---
    Task 3: Melting Ice with a Perfect Gas (17 points)

    Problem Setup:
    An isolated cylinder has two chambers: the bottom contains a perfect gas, and the top an ice-water mixture (EW) at phase equilibrium. A heat-conducting, massless membrane separates them. A frictionless piston of mass \( m_K = 32 \, \text{kg} \) rests atop the EW and exerts pressure against atmospheric conditions (\( p_{\text{amb}} = 1 \, \text{bar} \)). Diameter of the cylinder is \( D = 10 \, \text{cm} \).

    Initial state:
    - Gas: \( T_{g,1} = 500^\circ\text{C} \), \( V_{g,1} = 3.14 \, \text{L} \)
    - EW: \( m_{\text{EW}} = 0.1 \, \text{kg} \), \( T_{\text{EW},1} = 0^\circ\text{C} \), ice mass fraction \( x_{\text{ice},1} = 0.6 \)

    Due to the temperature difference, heat flows from gas to EW, melting some ice. Final state 2 is reached when no more heat is exchanged.

    Assumptions:
    - The gas is ideal with \( c_V = 0.633 \, \text{kJ/kg·K} \), molar mass \( M_g = 50 \, \text{kg/kmol} \).
    - Ice and water are incompressible; phase change does not alter volume.
    - Kinetic and potential energies are negligible.
    - In state 2, gas and EW are in thermal equilibrium.
    - The membrane and piston move without friction.

    Figure Description:
    Figure 4 depicts state 1 and 2 with labeled geometry, pressures, and temperatures.

    Subtasks:
    a) Determine the gas pressure \( p_{g,1} \) and mass \( m_g \) in state 1.

    b) Given \( x_{\text{ice},2} > 0 \), what are \( T_{g,2} \), \( p_{g,2} \)? Justify in one sentence.

    c) Calculate the transferred heat \( Q_{12} \) from gas to EW between states 1 and 2.

    d) Determine the final ice fraction \( x_{\text{ice},2} \) in state 2 using the solid-liquid equilibrium table.

    ---
    Task 4: Freeze Drying with R134a Cycle (18.5 points)

    Problem Setup:
    The freeze-drying process for food operates in two steps:

    Step i:
    The food is placed in the freeze dryer pre-cooled to \( T_i \). Heat \( \dot{Q}_K \) is removed via a heat exchanger using R134a, undergoing full isobaric evaporation 6 K below \( T_i \). A reversible adiabatic compressor raises pressure to 8 bar (state 3). The refrigerant is then fully condensed isobarically (state 4) and expanded adiabatically (state 1).

    Step ii:
    The chamber pressure is reduced 5 mbar below the triple point of water to cause sublimation. \( T_i \) is held 10 K above the sublimation temperature.

    Assumptions:
    - Cooling cycle subtasks: 4b to 4d. Tasks 4a and 4e are independent.
    - Use Figure 6 (p-T diagram) to find \( T_i \).
    - Use Tables A-10 to A-12 for R134a data.
    - \( T_i \) is constant and homogeneous.
    - The system is adiabatic to surroundings.
    - All processes in Step i are stationary.
    - Kinetic and potential energies are negligible.

    Figure Description:
    Figure 5 shows the freeze-drying system and refrigeration loop with states labeled.

    Subtasks:
    a) Draw the freeze-drying process (steps i and ii) in a p-T diagram. Label phase regions. Do not use Figure 6.

    b) Determine the required refrigerant mass flow rate \( \dot{m}_{\text{R134a}} \).

    c) Determine the vapor quality \( x_1 \) of the refrigerant at state 1 after expansion.

    d) Calculate the coefficient of performance:
    \[
    \epsilon_K = \frac{\dot{Q}_K}{\dot{W}_K}
    \]

    e) How would \( T_i \) evolve in Step ii if the cooling cycle from Step i continued with constant \( \dot{Q}_K \)? Justify your answer.
    """
# === Load environment variables from .env ===
load_dotenv()

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL")
print(f"Model name: {MODEL_NAME}")

# === Functions ===
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def update_last_known_task(model_output, previous_task):
    matches = re.findall(r"TASK\s+(\d+[a-zA-Z]?)", model_output, flags=re.IGNORECASE)
    return matches[-1] if matches else previous_task

def extract_student_id(image_path):
    match = re.match(r"(\d{3})_\d+", image_path.stem)
    return match.group(1) if match else None

def build_user_prompt(base64_image, last_known_task):
    return [
        {
            "type": "text",
            "text": (
                # PROMPT FOR NATURAL LANGUAGE TRANSCRIPTION
                # "The attached image is a handwritten page from a student's exam.\n\n"
                # "Transcribe only what is clearly visible in the image into clear, natural English.\n\n"
                # "🔹 Task Labeling Rules:\n"
                # "- Always respect the task number written on the page (e.g., 'Aufgabe 2' must be labeled as 'TASK 2a'). Never downgrade to a lower number like '1a'.\n"
                # "- Use headers like `TASK 1a`, `TASK 2b`, etc. **only if** those labels (or equivalents like `Aufgabe 2b`) appear clearly in the image.\n"
                # "- If only a general label like `Task 1` or `Aufgabe 1` is written, assign all content to `TASK 1a` only — do not split into 1b, 1c, etc.\n"
                # "- If the task is labeled only with a number (e.g., `2`), assign it as `TASK 2a`.\n"
                # "- If only a letter is written (e.g., `c)`), continue from the previous task (e.g., `3b` → `3c`) **but only if it's in a valid range**.\n"
                # f"- If there is **no task label visible at all**, continue from the previous task: '{last_known_task}'.\n"
                # "- Use also the testquestions provided in the system message to help with labeling ambiguous or partial answers.\n"
                # "- Do not invent or split tasks based on layout or assumptions."
                # "🔹 Content Instructions:\n"
                # "- Transcribe exactly what is written.\n"
                # "- If the content is not clear, use the provided context to interpret it.\n"
                # "- Write equations in full words (e.g., `x^2 + 2x` → 'x squared plus two x').\n"
                # "- Describe diagrams or graphs clearly.\n"
                # "- Ignore anything that is clearly crossed out.\n"
                # "- Do not say 'the student writes' — just describe the content directly.\n\n"
                # "🔹 Output Format:\n"
                # "TASK <label>\n"
                # "<transcribed content>\n\n"
                # "If the page has no content, return:\n"
                # "`No content found.`"

                # PROMPT FOR LATEX TRANSCRIPTION
                "The attached image is a handwritten page from a student's exam.\n\n"
                "🔹 Transcription Instructions:\n"
                "- Transcribe only what is clearly visible in the image.\n"
                "- Write all textual explanations in clear, natural English.\n"
                "- Write all **mathematical expressions using proper LaTeX formatting**.\n"
                "- Describe diagrams, graphs, or drawings clearly in words.\n"
                "- Ignore anything that is clearly crossed out.\n"
                "- Do not say 'the student writes' — just describe the content directly.\n\n"

                "🔹 Task Labeling Rules:\n"
                "- Always respect the task number written on the page (e.g., 'Aufgabe 2' must be labeled as 'TASK 2a'). Never relabel as '1a'.\n"
                "- Use headers like `TASK 1a`, `TASK 2b`, etc. **only if** those labels (or equivalents like `Aufgabe 2b`) appear clearly in the image.\n"
                "- If only a general label like `Task 1` or `Aufgabe 1` is written, assign all content to `TASK 1a` only — do not split into 1b, 1c, etc.\n"
                "- If the task is labeled only with a number (e.g., `2`), assign it as `TASK 2a`.\n"
                "- If only a letter is written (e.g., `c)`), continue from the previous task (e.g., `3b` → `3c`) **but only if it's in a valid range**.\n"
                "- If there is **no task label visible at all**, continue from the previous task: '{last_known_task}'.\n"
                "- Use also the test questions provided in the system message to help with labeling ambiguous or partial answers.\n"
                "- Do not invent or split tasks based on layout or assumptions.\n\n"

                "🔹 Output Format:\n"
                "TASK <label>\n"
                "<transcribed text (natural English)>\n"
                "<LaTeX-formatted math expressions>\n"
                "<description of diagrams/graphs in words>\n\n"
                "If the page has no content, return:\n"
                "`No content found.`"
            )
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        }
    ]

def process_image(image_path, client, last_known_task):
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    # "You are an OCR and document understanding assistant. Your job is to transcribe handwritten student exam pages into fully structured, natural English.\n\n"
                    # "Only describe what is visually present on the page.\n"
                    # "Below are the exam questions for reference, to help with interpreting ambiguous or partial answers:\n"
                    # f"{EXAM_QUESTIONS_Latex}"
                    f"""
                    You are an OCR and document understanding assistant. Your job is to transcribe handwritten student exam pages into fully structured, natural English.

                    🔹 Transcription Rules:
                    - Transcribe only what is clearly visible and legible on the page.
                    - Write all explanatory or descriptive text in **natural English**.
                    - Write all **mathematical expressions using LaTeX formatting** (e.g., `\\frac{{a}}{{b}}`, `x^2`, `\\Delta S`).
                    - Describe any **graphs, sketches, or figures** in words.
                    - Ignore anything that is clearly crossed out.

                    🔹 Task Labeling Rules:
                    - Always use the task number shown on the page (e.g., "Aufgabe 2" → `TASK 2a`). Never relabel or downgrade (e.g., don’t write `TASK 1a`).
                    - If only a general label like `Task 1` or `Aufgabe 1` is visible, assign all content to `TASK 1a`.
                    - If the task is labeled only with a number (e.g., `2`), assign it as `TASK 2a`.
                    - If only a letter appears (e.g., `c)`), continue from the last known task (e.g., `3b` → `3c`) **if valid**.
                    - If **no task label** is visible, continue from the last known task: '{{last_known_task}}'.
                    - Do not infer or split content based on layout or guesswork.

                    🔹 Output Format:
                    TASK <label>
                    <transcribed natural English text and LaTeX-formatted math>
                    <verbal description of figures/graphs>

                    If no content is visible on the page, return:
                    `No content found.`

                    Use the following exam questions as reference to help interpret ambiguous or partial content:

                    {EXAM_QUESTIONS_Latex}
                    """

                )
            },
            {
                "role": "user",
                "content": build_user_prompt(base64_image, last_known_task)
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

def save_result(text, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    print(f"Result saved to: {output_path}")

def process_folder(input_folder):
    input_folder = Path(input_folder)
    output_folder = input_folder.parent / f"{input_folder.name}_Latex"
    output_folder.mkdir(parents=True, exist_ok=True)

    client = AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT
    )
    print(MODEL_NAME)
    student_images = defaultdict(list)
    for path in input_folder.glob("*.jpg"):
        match = re.match(r"(\d{3})_(\d+)", path.stem)
        if match:
            student_id, page_num = match.groups()
            student_images[student_id].append((int(page_num), path))

    for student_id in student_images:
        student_images[student_id] = sorted(student_images[student_id])

    image_files = [path for _, paths in sorted(student_images.items()) for _, path in paths]

    last_known_task_by_student = defaultdict(lambda: None)
    count = 0
    max_count = len(image_files)
    for image_path in image_files:
        student_id = extract_student_id(image_path)
        if not student_id:
            print(f"Skipping file with invalid name: {image_path.name}")
            continue

        print(f"{count}/{max_count} Processing {image_path.name}...")
        last_task = last_known_task_by_student[student_id]
        result_text = process_image(image_path, client, last_task)

        updated_task = update_last_known_task(result_text, last_task)
        last_known_task_by_student[student_id] = updated_task

        output_file = output_folder / f"{image_path.stem}.tex"
        save_result(result_text, output_file)
        time.sleep(0.5)
        count += 1
    print(f"All files processed. Results saved in {output_folder}")

# === Main ===
if __name__ == "__main__":
    FOLDER_PATH = "PDF_to_NatLan/JPGs"
    process_folder(FOLDER_PATH)
    print("Processing complete.")