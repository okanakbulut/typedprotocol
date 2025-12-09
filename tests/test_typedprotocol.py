import typing
import pytest
from typedprotocol import TypedProtocol


# Test protocols
class Request(TypedProtocol): 
    id: int
    data: bytes


class Custom(Request):
    name: str


class ServiceProtocol(TypedProtocol):
    name: str
    
    def process(self, data: bytes) -> str: ...
    
    def validate(self, value: int) -> bool: ...


class AsyncServiceProtocol(TypedProtocol):
    async def fetch_data(self, url: str) -> dict[str, typing.Any]: ...

class ParamType(TypedProtocol):
    value: int
    label: str

class ExtendedParamType(ParamType):
    extra: float

class ComplexServiceProtocol(TypedProtocol):
        def compute(self, param: ParamType) -> int: ...


class TestGenericProtocols:
    """Test protocols with generic type variables."""

    def test_generic_protocol_inheritance(self):
        T = typing.TypeVar('T')
        U = typing.TypeVar('U')
        
        # Base generic protocol
        class BaseProtocol(TypedProtocol[T]):
            data: T
            def process(self, item: T) -> T: ...
        
        # Extended generic protocol that inherits from base with different TypeVar
        # BaseProtocol[U] means T gets substituted with U in the base protocol
        class ExtendedProtocol(BaseProtocol[U]):
            metadata: str
            def validate(self, item: U) -> bool: ...
        
        # Implementation that should work with ExtendedProtocol
        class StringProcessor:
            data: str
            metadata: str
            
            def process(self, item: str) -> str:
                return item.upper()
            
            def validate(self, item: str) -> bool:
                return len(item) > 0
        
        # Implementation with inconsistent types - should fail
        class MixedProcessor:
            data: str
            metadata: str
            
            def process(self, item: str) -> str:
                return item.upper()
            
            def validate(self, item: int) -> bool:  # Wrong type - U should be str!
                return item > 0
        
        assert issubclass(StringProcessor, ExtendedProtocol)
        assert not issubclass(MixedProcessor, ExtendedProtocol)
        

class TestMethodParameterProtocol:
    """Test method parameter with typed protocols."""
   
    def test_valid_parameter_protocol(self):
        class ValidComplexService:
            def compute(self, param: ParamType) -> int:
                return param.value * 2
        
        assert issubclass(ValidComplexService, ComplexServiceProtocol)
    
    def test_invalid_parameter_protocol(self):
        class InvalidComplexService:
            def compute(self, param: ExtendedParamType) -> int:  # wrong parameter type
                return param.value * 2
        
        assert not issubclass(InvalidComplexService, ComplexServiceProtocol)


class TestAttributeProtocols:
    """Test protocols with only attributes."""
    
    def test_valid_implementation(self):
        class ValidImplementation:
            id: int
            data: bytes
            name: str
        
        assert issubclass(ValidImplementation, Custom)
    
    def test_missing_field(self):
        class MissingField:
            id: int
            name: str  # missing 'data' field
        
        assert not issubclass(MissingField, Request)
    
    def test_wrong_type(self):
        class WrongType:
            id: str  # should be int
            data: bytes
            name: str
        
        assert not issubclass(WrongType, Request)


class TestMethodProtocols:
    """Test protocols with methods."""
    
    def test_valid_service(self):
        class ValidService:
            name: str
            
            def process(self, data: bytes) -> str:
                return "processed"
            
            def validate(self, value: int) -> bool:
                return True
        
        assert issubclass(ValidService, ServiceProtocol)
    
    def test_missing_method(self):
        class MissingMethod:
            name: str
            
            def process(self, data: bytes) -> str:
                return "processed"
            # missing validate method
        
        assert not issubclass(MissingMethod, ServiceProtocol)
    
    def test_wrong_method_signature(self):
        class WrongMethodSignature:
            name: str
            
            def process(self, data: str) -> str:  # wrong parameter type
                return "processed"
            
            def validate(self, value: int) -> bool:
                return True
        
        assert not issubclass(WrongMethodSignature, ServiceProtocol)
    
    def test_wrong_return_type(self):
        class WrongReturnType:
            name: str
            
            def process(self, data: bytes) -> int:  # wrong return type
                return 42
            
            def validate(self, value: int) -> bool:
                return True
        
        assert not issubclass(WrongReturnType, ServiceProtocol)


class TestAsyncMethodProtocols:
    """Test protocols with async methods."""
    
    def test_valid_async_service(self):
        class ValidAsyncService:
            async def fetch_data(self, url: str) -> dict[str, typing.Any]:
                return {"result": "data"}
        
        assert issubclass(ValidAsyncService, AsyncServiceProtocol)
    
    def test_wrong_async_signature(self):
        class WrongAsyncSignature:
            def fetch_data(self, url: str) -> dict[str, typing.Any]:  # not async
                return {"result": "data"}
        
        assert not issubclass(WrongAsyncSignature, AsyncServiceProtocol)


class TestTypeCompatibility:
    """Test type compatibility and subclass relationships."""
    
    def test_subclass_type_method(self):
        class SubclassTypeMethod:
            name: str
            
            def process(self, data: bytes) -> str:
                return "processed"
            
            def validate(self, value: bool) -> bool:  # bool is subclass of int
                return True
        
        assert issubclass(SubclassTypeMethod, ServiceProtocol)


class TestExtraMembers:
    """Test implementations with extra fields and methods."""
    
    def test_extra_fields_implementation(self):
        class ExtraFieldsImplementation:
            # Required by Request protocol
            id: int
            data: bytes
            
            # Extra fields (should be allowed)
            extra_string: str
            extra_number: float
            extra_list: list[int]
        
        assert issubclass(ExtraFieldsImplementation, Request)
    
    def test_extra_methods_implementation(self):
        class ExtraMethodsImplementation:
            # Required by ServiceProtocol
            name: str
            
            def process(self, data: bytes) -> str:
                return "processed"
            
            def validate(self, value: int) -> bool:
                return True
            
            # Extra methods (should be allowed)
            def extra_method(self, x: int) -> str:
                return f"extra: {x}"
            
            def another_extra(self) -> None:
                pass
        
        assert issubclass(ExtraMethodsImplementation, ServiceProtocol)
    
    def test_extra_fields_and_methods_implementation(self):
        class ExtraFieldsAndMethodsImplementation:
            # Required by ServiceProtocol
            name: str
            
            def process(self, data: bytes) -> str:
                return "processed"
            
            def validate(self, value: int) -> bool:
                return True
            
            # Extra fields
            extra_field: str
            count: int
            
            # Extra methods
            def helper_method(self, data: str) -> int:
                return len(data)
            
            def cleanup(self) -> None:
                pass
        
        assert issubclass(ExtraFieldsAndMethodsImplementation, ServiceProtocol)
    
    def test_implements_multiple_with_extras(self):
        class ImplementsMultipleWithExtras:
            # Required by Request
            id: int
            data: bytes
            
            # Required by ServiceProtocol  
            name: str
            
            def process(self, data: bytes) -> str:
                return "processed"
            
            def validate(self, value: int) -> bool:
                return True
            
            # Extra members
            extra_attr: dict[str, typing.Any]
            
            def extra_async_method(self) -> typing.Awaitable[str]:
                async def inner():
                    return "async result"
                return inner()
        
        assert issubclass(ImplementsMultipleWithExtras, Request)
        assert issubclass(ImplementsMultipleWithExtras, ServiceProtocol)


class TestMultipleClassParameters:
    """Test issubclass with multiple class parameters."""
    
    def test_only_request_impl(self):
        class OnlyRequestImpl:
            id: int
            data: bytes
        
        assert issubclass(OnlyRequestImpl, Request)
        assert not issubclass(OnlyRequestImpl, ServiceProtocol)
        assert issubclass(OnlyRequestImpl, (Request, ServiceProtocol))
    
    def test_only_service_impl(self):
        class OnlyServiceImpl:
            name: str
            
            def process(self, data: bytes) -> str:
                return "processed"
            
            def validate(self, value: int) -> bool:
                return True
        
        assert not issubclass(OnlyServiceImpl, Request)
        assert issubclass(OnlyServiceImpl, ServiceProtocol)
        assert issubclass(OnlyServiceImpl, (Request, ServiceProtocol))
    
    def test_both_protocols_impl(self):
        class BothProtocolsImpl:
            # Implements both Request and ServiceProtocol
            id: int
            data: bytes
            name: str
            
            def process(self, data: bytes) -> str:
                return "processed"
            
            def validate(self, value: int) -> bool:
                return True
        
        assert issubclass(BothProtocolsImpl, Request)
        assert issubclass(BothProtocolsImpl, ServiceProtocol)
        assert issubclass(BothProtocolsImpl, (Request, ServiceProtocol))
    
    def test_neither_impl(self):
        class NeitherImpl:
            some_field: str
        
        assert not issubclass(NeitherImpl, Request)
        assert not issubclass(NeitherImpl, ServiceProtocol)
        assert not issubclass(NeitherImpl, (Request, ServiceProtocol))
    
    def test_mixed_protocol_and_regular_class(self):
        class RegularClass:
            pass
        
        class OnlyRequestImpl:
            id: int
            data: bytes
        
        assert issubclass(OnlyRequestImpl, (Request, RegularClass))
        assert issubclass(OnlyRequestImpl, (RegularClass, Request))
    
    def test_three_protocols(self):
        class BothProtocolsImpl:
            # Implements both Request and ServiceProtocol
            id: int
            data: bytes
            name: str
            
            def process(self, data: bytes) -> str:
                return "processed"
            
            def validate(self, value: int) -> bool:
                return True
        
        assert issubclass(BothProtocolsImpl, (Request, ServiceProtocol, AsyncServiceProtocol))


class TestInheritanceRestrictions:
    """Test protocol inheritance restrictions."""
    
    def test_valid_protocol_inheritance(self):
        # This should work - protocol inheriting from protocol
        class ValidProtocolInheritance(Request):
            extra_field: str
        
        assert ValidProtocolInheritance.__name__ == "ValidProtocolInheritance"
    
    def test_invalid_protocol_inheritance_regular_class(self):
        # This should fail - protocol inheriting from regular class
        class RegularClass:
            pass
        
        with pytest.raises(TypeError, match="cannot inherit from non-protocol type"):
            class InvalidProtocolInheritance(RegularClass, TypedProtocol): # type: ignore
                field: int
    
    def test_invalid_builtin_inheritance(self):
        # This should fail - protocol inheriting from built-in type
        with pytest.raises(TypeError, match="cannot inherit from non-protocol type"):
            class InvalidBuiltinInheritance(dict, TypedProtocol): # type: ignore
                field: int
    
    def test_multiple_protocol_inheritance(self):
        # This should work - multiple protocol inheritance
        class MultiProtocolInheritance(Request, ServiceProtocol):
            extra: float
        
        assert MultiProtocolInheritance.__name__ == "MultiProtocolInheritance"


class TestAnnotationEnforcement:
    """Test annotation enforcement for protocols."""
    
    def test_missing_attribute_annotation(self):
        # This should fail - missing attribute annotation
        with pytest.raises(TypeError, match="must have a type annotation"):
            class MissingAttributeAnnotation(TypedProtocol): # type: ignore
                unannotated_attr = "some_value"  # This should fail

                def process(self, data: bytes) -> str: ...
    
    def test_missing_parameter_annotation(self):
        # This should fail - method without parameter annotation
        with pytest.raises(TypeError, match="must have a type annotation"):
            class MissingParameterAnnotation(TypedProtocol): # type: ignore
                name: str

                def process(self, data) -> str: ...  # missing parameter annotation # type: ignore
    
    
    def test_properly_annotated_protocol(self):
        # This should work - properly annotated protocol
        class ProperlyAnnotatedProtocol(TypedProtocol):
            name: str
            count: int
            
            def process(self, data: bytes) -> str: ...
            def validate(self, value: int) -> bool: ...
            def notify(self, message: str) -> None: ...  # procedures with None return
        
        assert ProperlyAnnotatedProtocol.__name__ == "ProperlyAnnotatedProtocol"


class TestInstantiationPrevention:
    """Test that protocols cannot be instantiated."""
    
    def test_typed_protocol_instantiation(self):
        with pytest.raises(TypeError, match="Cannot instantiate protocol class"):
            TypedProtocol()
    
    def test_request_instantiation(self):
        with pytest.raises(TypeError, match="Cannot instantiate protocol class"):
            Request()
    
    def test_service_protocol_instantiation(self):
        with pytest.raises(TypeError, match="Cannot instantiate protocol class"):
            ServiceProtocol()
    
    def test_custom_instantiation(self):
        with pytest.raises(TypeError, match="Cannot instantiate protocol class"):
            Custom()