

from errors import SemanticError, AttributesError, TypesError, NamesError
from my_types import *
from tools import Context, Scope
import visitor
from utils import is_basic_type
from my_ast import *
from  simulation import VRP_Simulation
from agents import *
definiciones = {}

graph=None
mapa=""
budget=0
name=""

days=1

simulate=False
class Visitor:
    def __init__(self, context:Context, errors=[]):
        self.context:Context = context
        self.current_type:Type = None
        self.errors:list = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node:ProgramNode,scope:Scope=Scope()):
        #self.context = Context()
        self.context.types['String'] = StringType()
        self.context.types['Int'] = IntType()
        self.context.types['Object'] = ObjectType()
        self.context.types['Bool'] = BoolType()
        self.context.types['SELF_TYPE'] = SelfType()
        self.context.types['IO'] = IOType()
        days=node.days
        simulate=node.simulate
        self.visit(node.map_block,scope.create_child())
        self.visit(node.stops_block,scope.create_child())
        self.visit(node.vehicle_type_block,scope.create_child())
        self.visit(node.clients_block,scope.create_child())
        self.visit(node.company_block,scope.create_child())
        self.visit(node.demands_block,scope.create_child())
        
        
    def _define_default_value(self, typex, node):
            if typex == IntType():
                node.expr = ConstantNumNode(0)
            elif typex == StringType():
                node.expr = ConstantStrNode("")
            elif typex == BoolType():
                node.expr = ConstantBoolNode('false')
            else:
                node.expr = ConstantVoidNode(node.id)
    
    @visitor.when(MapNode)
    def visit(self, node:MapNode,scope:Scope):
        mapa = node.map
        self.visit(node.map)
    
    @visitor.when(StopsNode)
    def visit(self, node:StopsNode,scope:Scope):
        for dec in node.stop_declarations:
            self.visit(dec,scope)
        
    @visitor.when(StopDeclarationNode)
    def visit(self, node:StopDeclarationNode,scope:Scope):
        #simulation.add_stop(node.identifier, node.address, node.people)
        pass
        
    @visitor.when(VehicleTypeNode)
    def visit(self, node:VehicleTypeNode,scope:Scope):
        for dec in node.declarations:
            self.visit(dec,scope)
    
    @visitor.when(VehicleTypeDeclarationNode)
    def visit(self, node:VehicleTypeDeclarationNode,scope:Scope):
        #simulation.add_vehicle_type(node.type)
        pass
    
    @visitor.when(ClientsNode)
    def visit(self, node:ClientsNode,scope:Scope):
        for dec in node.client_declarations:
            self.visit(dec,scope)
            
    @visitor.when(ClientDeclarationNode)
    def visit(self, node:ClientDeclarationNode,scope:Scope):
       # simulation.add_client(node.identifier, node.name, node.stops,node.depot)
       pass
        
    @visitor.when(CompanyBlockNode)
    def visit(self, node:CompanyBlockNode,scope:Scope):
        budget=node.budget
        #simulation.direction_depot(node.depot)
        for dec in node.vehicle_declarations:
            self.visit(dec,scope)
            
    @visitor.when(CompanyDeclarationNode)
    def visit(self, node:CompanyDeclarationNode,scope:Scope):
        for dec in node.vehicle_declarations:
            self.visit(dec,scope)
            # Recupera el valor de la variable del nodo VarDeclarationNode
            value = dec.value
            type = dec.type
            # Pasa el valor como argumento al m??todo add_vehicle de la simulaci??n
            #simulation.add_vehicle(type, node.identifier, value)
            
    @visitor.when(DemandsNode)
    def visit(self, node:DemandsNode,scope:Scope):
        for dec in node.demands:
            self.visit(dec,scope)
        if simulate:
            company=Company(name,budget,mapa)
            VRP_Simulation(graph,Company,days)
    
    
    def add_function(id, params, return_type, body):
        def function(*args, **kwargs):
            exec(body)
            function.__code__ = compile(body, "<string>", "exec")
        return function
        
    @visitor.when(FuncDeclarationNode)
    def visit(self, node:FuncDeclarationNode,scope:Scope):
        args_names = []
        args_types = []
        self.current_type = node.type
        # parent = self.current_type.parent 
        # pnames = [param[0] for param in node.params]
        # ptypes = [param[1] for param in node.params]

        new_scope = scope.create_child()
        scope.functions[node.id] = new_scope

        # A??adir las variables de argumento
        for pname, ptype in node.params:
            if pname == 'self':
                self.errors.append(SemanticError(SemanticError.SELF_PARAM, *ptype.pos)) 
                args_names.append(pname)
            
            try:
                arg_type = self.context.get_type(ptype.value, ptype.pos)
            except SemanticError:
                error_text = TypesError.PARAMETER_UNDEFINED % (ptype.value, ptype.value)
                self.errors.append(TypesError(error_text, *ptype.pos))
                arg_type = ErrorType()
            args_types.append(arg_type)
            
        # try:
        return_type = node.type
        # except SemanticError as e:
        #     error_text = TypesError.RETURN_TYPE_UNDEFINED % (node.type, node.id)
        #     self.errors.append(TypesError(error_text, *node.type_pos))
        #     return_type = ErrorType(node.type_pos)
    
        try:
            self.current_type.define_method(node.id, args_names, args_types, return_type, node.pos)
        except SemanticError as e:
            self.errors.append(e)
            new_scope.define_variable(pname, self._get_type(ptype.value, ptype.pos))
            
    
        id = node.id
    # Accede a los par??metros de la funci??n a trav??s de la propiedad 'params' del nodo
        params = node.params
    # Accede al tipo de retorno de la funci??n a trav??s de la propiedad 'type' del nodo
        return_type = node.type
        new_scope = scope.create_child()
        visited_body = self.visit(node.body, new_scope)
        function =self.add_function(params, return_type, visited_body)
        definiciones[id]= [scope,function]
        self.current_method = self.current_type.get_method(node.id, node.pos)
        
        # self.visit(node.body, new_scope)
  
        
    @visitor.when(StaticCallNode)
    def visit(self, node:StaticCallNode,scope:Scope):
        evaluated_args = [self.visit(arg) for arg in node.args]
        if node.id in definiciones:
            definiciones[node.id,scope](*evaluated_args)
        else:
            raise SemanticError("La funci??n no existe")
    
    @visitor.when(AttrDeclarationNode)
    def visit(self, node:AttrDeclarationNode,scope:Scope):
        attr = self.current_type.get_attribute(node.id, node.pos)
        if node.expr is None:
            self._define_default_value(attr.type, node)
        else:
            self.visit(node.expr, scope)
        attr.expr = node.expr
        scope.define_attribute(attr)

# class VarVisitor:
#     def __init__(self, context=Context, errors=[]):
#         self.context = context
#         self.current_type = None
#         self.current_method = None
#         self.errors = errors
#         self.current_index = None # Lleva 
        
#     @visitor.on('node')
#     def visit(self, node, scope):
#         pass

#     @visitor.when(ProgramNode)
#     def visit(self, node:ProgramNode, scope:Scope=None):
#         scope = Scope()
#         for declaration in node.declarations:
#             self.visit(declaration, scope.create_child())
#         return scope

    def _get_type(self, ntype, pos):
        try:
            return self.context.get_type(ntype, pos)
        except SemanticError as e:
            self.errors.append(e)
            return ErrorType()
        
    def copy_scope(self, scope:Scope, parent:Type):
        if parent is None:
            return
        for attr in parent.attributes.values():
            if scope.find_variable(attr.name) is None:
                scope.define_attribute(attr)
        self.copy_scope(scope, parent.parent)


        
    
    @visitor.when(VarDeclarationNode)
    def visit(self, node:VarDeclarationNode, scope:Scope):
        if node.id == 'self':
            error_text = SemanticError.SELF_IN_LET
            self.errors.append(SemanticError(error_text, *node.pos))
            return

        try:
            vtype = self.context.get_type(node.type, node.pos)
        except SemanticError:
            error_text = TypesError.UNDEFINED_TYPE_LET % (node.type, node.id)
            self.errors.append(TypesError(error_text, *node.type_pos))
            vtype = ErrorType()

        vtype = self._get_type(node.type, node.type_pos)
        var_info = scope.define_variable(node.id, vtype)
       
        if node.expr is not None:
            self.visit(node.expr, scope)
        else:
            self._define_default_value(vtype, node)
            
        
    @visitor.when(AssignNode)
    def visit(self, node:AssignNode, scope:Scope):
        if node.id == 'self':
            error_text = SemanticError.SELF_IS_READONLY
            self.errors.append(SemanticError(error_text, *node.pos))
            return
    
        vinfo = scope.find_variable(node.id)
        if vinfo is None:
            var_info = scope.find_attribute(node.id)
            if var_info is None:
                error_text = NamesError.VARIABLE_NOT_DEFINED %(node.id)  
                self.errors.append(NamesError(error_text, *node.pos))
                vtype = ErrorType()
                scope.define_variable(node.id, vtype)
            
        self.visit(node.expr, scope)
    
    # @visitor.when(BlockNode)
    # def visit(self, node:BlockNode, scope:Scope):
    #     for exp in node.expr_list:
    #         self.visit(exp, scope)
    

    @visitor.when(LetNode)
    def visit(self, node:LetNode, scope:Scope):
        n_scope = scope.create_child()
        scope.expr_dict[node] = n_scope
        for init in node.init_list:
            self.visit(init, n_scope)
        
        self.visit(node.expr, n_scope)

    #no necesario
    @visitor.when(BinaryNode)
    def visit(self, node:BinaryNode, scope:Scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)

     
    @visitor.when(UnaryNode)
    def visit(self, node:UnaryNode, scope:Scope):
        self.visit(node.expr, scope)
     

    @visitor.when(VariableNode)
    def visit(self, node:VariableNode, scope:Scope):
        try:
            return self.current_type.get_attribute(node.lex, node.pos).type
        except AttributesError:
            if not scope.is_defined(node.lex):
                error_text = NamesError.VARIABLE_NOT_DEFINED %(node.lex)
                self.errors.append(NamesError(error_text, *node.pos))
                vinfo = scope.define_variable(node.lex, ErrorType(node.pos))
            else:
                vinfo = scope.find_variable(node.lex)
            return vinfo.type


    @visitor.when(WhileNode)
    def visit(self, node:WhileNode, scope:Scope):
        self.visit(node.cond, scope)
        self.visit(node.expr, scope)


    @visitor.when(ConditionalNode)
    def visit(self, node:ConditionalNode, scope:Scope):
        self.visit(node.cond, scope)
        self.visit(node.stm, scope)
        self.visit(node.else_stm, scope)

    @visitor.when(IsVoidNode)
    def visit(self, node:IsVoidNode, scope:Scope):
        self.visit(node.expr, scope)
    
    @visitor.when(CallNode)
    def visit(self, node:CallNode, scope:Scope):
        self.visit(node.obj, scope)
        args=[]
        for arg in node.args:
            args.append(self.visit(arg, scope))
        definiciones[node.id](*args)


    @visitor.when(BaseCallNode)
    def visit(self, node:BaseCallNode, scope:Scope):
        self.visit(node.obj, scope)
        for arg in node.args:
            self.visit(arg, scope)
    

    @visitor.when(StaticCallNode)
    def visit(self, node:StaticCallNode, scope:Scope):
        args=[]
        for arg in node.args:
            args.append(self.visit(arg, scope))
            if args[0] == []:
                args = [arg.lex]
        if self.current_type.name == 'IO':
                if node.id == 'out_string':
                    self.current_type.out_string(args)
                elif node.id == 'out_int':
                    self.current_type.methods['out_int'](args)
        else:
            definiciones[node.id](*args)
       


   
    # @visitor.when(CaseNode)
    # def visit(self, node:CaseNode, scope:Scope):
    #     self.visit(node.expr, scope)

    #     new_scp = scope.create_child()
    #     scope.expr_dict[node] = new_scp

    #     for case in node.case_list:
    #         self.visit(case, new_scp.create_child())
        

    @visitor.when(OptionNode)
    def visit(self, node:OptionNode, scope:Scope):
        try:
            typex = self.context.get_type(node.typex, node.type_pos)
        except TypesError:
            error_txt = TypesError.CLASS_CASE_BRANCH_UNDEFINED % node.typex
            self.errors.append(TypesError(error_txt, *node.type_pos))
            typex = ErrorType()

        scope.define_variable(node.id, typex)
        self.visit(node.expr, scope)